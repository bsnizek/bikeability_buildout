# -*- coding: UTF-8 -*-

######################################################################################
#
# bikeability.dk
#
# Copyright (c) 2010 Snizek & Skov-Pedersen
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# this program; if not, see <http://www.gnu.org/licenses/>.
#
######################################################################################

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from config import *
from geoalchemy import Table, GeometryColumn, Geometry, LineString, Point, GeometryDDL, GeometryExtensionColumn, GeometryCollection, DBSpatialElement, WKTSpatialElement, WKBSpatialElement
from geoalchemy.postgis import PGComparator, pg_functions
from osgeo import ogr,osr
from plone.memoize.view import memoize
from random import random
from sqlalchemy import create_engine, MetaData, Column, Integer, Numeric, String, Boolean, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from zope.app.component.hooks import getSite
import csv
import pprint
import string
import sys
import transaction

class SaveAllPolylines(BrowserView):
    """
    """
    
    template = ViewPageTemplateFile('templates/save_shp_file.pt')
    rspd_ids = []
    # lets build the ORM stuff
    if SAVE_INTO_POSTGRESQL:
        engine = create_engine(POSTGRESQL_CONNECTION_STRING, echo = ECHO)
        metadata = MetaData(engine)
        session = sessionmaker(bind=engine)()
        Base = declarative_base(metadata=metadata)
    
#        person_table = Table('person', metadata,
#                              Column('rspdid', Integer, primary_key=True),
#                              Column('sex', String),
#                              Column('last_biketour_duration', Numeric) # duration of the person's last biketour,
#                              
#                              )    
    
        class Person(Base):
            """The ORM class corresponding to the line in Suzanne's questionnaire data
            """
            
            __tablename__ = "person"
            __table_args__ = {'extend_existing':True}
            rspdid = Column(Integer, primary_key=True)   
            sex = Column(String)
            last_biketour_duration = Column(String)
            birth_year = Column(String)
            income = Column(String)
            
            def __init__(self, rspdid, 
                         income = None,
                         last_biketour_duration = None,
                         sex  =None,
                         birth_year = None):
                
                self.rspdid = rspdid
                self.sex = sex
                self.last_biketour_duration = last_biketour_duration
                self.birth_year = birth_year
                
            def __repr__(self):
                print "<Person nummer %d" % rspdid
            
#        mapper(Person, person_table)
        
        class PGPoly(Base):
            """The ORM class corresponding to the "poly" table 
            """
            __tablename__ = 'poly'
            
            gid = Column(Integer, Sequence('poly_gid_sequence'), primary_key=True)
            rspdid = Column(Integer, ForeignKey("person.rspdid"))
            
            # calculated fields
            length = Column(Numeric)                            # the number into this one (calculated by ...)
            number_of_edges = Column(Integer)                   # the number of edges (calculated by ...)
            average_edge_length = Column(Numeric)               # the average length of an edge (calculated by ...)
            number_of_edge_crosses = Column(Integer)            # the number of loops, i.e. the polyline crosses itself 
            
            the_geom = GeometryColumn(Geometry(2), 
                                      comparator=PGComparator, 
                                      nullable=True)
            
            # calculated booleans and standard line measures
            no_points = Column(Boolean) 
            is_ring = Column(Boolean)
            only_one_edge = Column(Boolean)                     # true if the polyline consists of only one segment or edge
            
    
        class PGPoint(Base):
            """The ORM class corresponding to the "point" table 
            """
            __tablename__ = 'point'
            
            gid = Column(Integer, Sequence('point_gid_sequence'), primary_key=True)
            rspdid = Column(Integer, ForeignKey("person.rspdid"))
            type = Column(String)
            t_nmbr = Column(Integer)
            dropdown = Column(String)
            text = Column(String)
            the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)
            polyline = ForeignKey('employees.employee_id')
            
        GeometryDDL(PGPoly.__table__)
        GeometryDDL(PGPoint.__table__)
        
    
    def __call__(self):
        """
        """   
        if  SAVE_AS_SHP:
            self.writePolylineShapeFile()
            
        if SAVE_INTO_POSTGRESQL:
            if CREATE_TABLES:
                self.createTables()
                
            self.loadQuestionnaireData()
            self.saveToPostresql()
        
        return self.template()
        
    def __init__(self, context, request):
        """
        """
        super(BrowserView, self).__init__(context, request)

    def getValues(self, object):
        return object.getMeasurement() 
    
    def getText(self, n=0, type="good"):
        return self.data_dict.get("%s-text%d" % (type,n),"")   
    
    def getDrop(self, n=0, type="good"):    
        return self.data_dict.get("%s-drop%d" % (type,n),"")    
 
    def createTables(self):
        self.metadata.drop_all()
        self.metadata.create_all()

    def getInRef(self):
        inref = osr.SpatialReference()
        inref.ImportFromEPSG(4326)
        return inref
        
    def getOutRef(self):
        outref = osr.SpatialReference()
        # outref.SetFromUserInput("EPSG:25832")                                    # GCS_WGS_1984
        outref.ImportFromProj4("+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs") # ETRS_1989_UTM_Zone_32N
        return outref
        
    def loadQuestionnaireData(self):
        """
        """

        questionnaireReader = csv.reader(open('/Users/besn/git/bikeability_buildout/bikeability_buildout/data/csv/dataset.csv', 'rb'), delimiter=';', quotechar='"')
        
        cntr = 0
        
        for row in questionnaireReader:
            value_dict = {}
            if cntr ==0:
                # setup dict
                field_labels = row
            else:
                cntr_2 = 0
                for item in row:
                    value_dict[field_labels[cntr_2]] = item
                    cntr_2 += 1
                
                rspdid = value_dict["responde"]
                last_biketour_duration = value_dict["s_12"]
                sex = value_dict["s_38"]
                birth_year = value_dict["s_39"]
                income = value_dict["s_3"]
                try:
#                    import pdb;pdb.set_trace()
                    rspdid = int(rspdid)
                    self.session.add(self.Person(
                                                 rspdid,
                                                 last_biketour_duration = last_biketour_duration,
                                                 sex = sex,
                                                 birth_year = birth_year,
                                                 income = income
                                                 )
                                     )
                    
                    self.rspd_ids.append(rspdid)
                    try:
                        self.session.commit()
                    except:
                        print "Unexpected error:", sys.exc_info()[0]
                        import pdb;pdb.set_trace()
                except:
                    print "BUMMER : %s" % value_dict["responde"]

            cntr += 1
        
        
        print cntr, " objects loaded from CSV"
        
            
    def saveToPostresql(self):
        
        inref = self.getInRef()
        outref = self.getOutRef()
        transform = osr.CoordinateTransformation(inref, outref)
        
        # let's do the looping
        results = getToolByName(self.context, 'portal_catalog')(portal_type="Measurement")
        gid = 0
        wordle_text = ""
        
        for r in results:
            gid =  gid + 1
            print "WRITIN ENTITY %s  --  %d" % (r.id, gid)
            obj = r.getObject()
            
            values = self.getValues(obj)
            self.data_dict = eval(values)
            
            cont = True
            try:
                int(r.id )
            except:
                cont = False
            
            import pdb;pdb.set_trace()
            
            if cont and int(r.id) in self.rspd_ids:   
            
                raw_polyline = self.data_dict.get("polyline",'')
                pairs = raw_polyline.split(";")
                    
                line = ogr.Geometry(type=ogr.wkbLineString)
                
                pair_counter = 0
                edges = []
                
                for pair in pairs:
                
                    coords = pair.split(",")
                    
                    if coords != ['']:
                        
                        x = string.atof(coords[0])
                        y = string.atof(coords[1])
                        
                        line.AddPoint(y, x)
                        
                        # let us build an edge and add it to edges for later processing
                        if pair_counter > 1:
                            
                            edge = ogr.Geometry(type=ogr.wkbLineString)
                            edge.AddPoint(y0, x0)
                            edge.AddPoint(y, x)
                            edge.AssignSpatialReference(inref)
                            edge.Transform(transform)
                            edge.SetCoordinateDimension(2)
                            edges.append(edge)
                        
                        x0 = x
                        y0 = y
                        
                        pair_counter +=1
                          
                    
                line.AssignSpatialReference(inref)
                line.Transform(transform)
                line.SetCoordinateDimension(2)
                    
                if line.Length() == 0.0:
                    self.session.add(self.PGPoly(gid=gid,
                                                 rspdid= int(r.id ),
                                                 no_points=True,
                                                 number_of_edges = len(pairs) -1
                                                 )
                                     )
                else:
#
                    # calculate number_of_edge_crosses
                    number_of_edge_crosses = 0
                    for e in edges:
                        for f in edges:
                            if e.Crosses(f):
                                number_of_edge_crosses +=1
                                
                    # build the polyline and add it to the session

                    only_one_edge = pair_counter == 1

                    self.session.add(self.PGPoly(gid=gid,
                                                 rspdid= int(r.id ),
                                                 no_points=False,
                                                 the_geom = line.ExportToWkt(),
                                                 length = line.Length(),
                                                 number_of_edges = len(pairs) -1,
                                                 average_edge_length = line.Length() / (len(pairs) -1),
                                                 is_ring = line.IsRing(),
                                                 number_of_edge_crosses = number_of_edge_crosses,
                                                 only_one_edge = only_one_edge
                                                 )
                                     )
                    # commit after each add
                    self.session.commit()
            else:
                print "fluffing out ..."
                
                
            # and now to the points
                
            for type in ["good","bad"]:
                for n in [0,1,2]:
                    coords = self.getCoord(n=n, type=type)
                    if coords !='':
                        cont = True
                        try:
                            int(r.id )
                        except:
                            cont = False
                                    
                        if cont:            
                            coords = coords.split(",")
                            coords = [string.atof(x) for x in coords]
                            x = coords[0]
                            y = coords[1]
                            point = ogr.Geometry(type=ogr.wkbPoint)
                            point.AddPoint(y, x)
                            point.AssignSpatialReference(inref)
                            point.Transform(transform)
                            point.SetCoordinateDimension(2)
                            
                            text = self.getText(n=n, type=type)
                            drop = self.getDrop(n=n, type=type)
                            
                            wordle_text += " "
                            wordle_text += text
                            
                            if int(r.id ) in self.rspd_ids:
                            
                                self.session.add(
                                                 self.PGPoint(
                                                              rspdid= int(r.id ),
                                                              the_geom = point.ExportToWkt(),
                                                              type = type,
                                                              t_nmbr = n,
                                                              text = text,
                                                              dropdown = drop,
                                                            )
                                                 )
                                # commit after each add
                                self.session.commit()
            
        print wordle_text
                        


    def getCoord(self, n=0, type="good"):
        return self.data_dict.get("%s-coord%d" % (type,n),"")
