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
from osgeo import ogr,osr
from plone.memoize.view import memoize
from random import random
from sqlalchemy import create_engine, MetaData, Column, Integer, Numeric, String, Boolean
from sqlalchemy.orm import sessionmaker, mapper
from zope.app.component.hooks import getSite
import pprint
import string
import sys
import transaction
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy import Table, GeometryColumn, Geometry, LineString, Point, GeometryDDL, GeometryExtensionColumn, GeometryCollection, DBSpatialElement, WKTSpatialElement, WKBSpatialElement
from geoalchemy.postgis import PGComparator, pg_functions

class SaveAllPolylines(BrowserView):
    """
    """
    
    template = ViewPageTemplateFile('templates/save_shp_file.pt')
    
    # lets build the ORM stuff
    if SAVE_INTO_POSTGRESQL:
        engine = create_engine(POSTGRESQL_CONNECTION_STRING, echo = True)
        metadata = MetaData(engine)
        session = sessionmaker(bind=engine)()
        Base = declarative_base(metadata=metadata)
    
#        point_table = Table('point', metadata,
#                            Column( 'rspid', Integer, primary_key=True),
#                            # ...
#                            GeometryExtensionColumn('the_geometry', Geometry(2))
#                            )

    
        class PGPoint(Base):
            """The ORM class corresponding to the "point" table 
            """
            __tablename__ = 'point'
            gid = Column(Integer, primary_key=True)
            rspdid = Column(Integer)
            type = Column(String)
            t_nmbr = Column(Integer)
            text = Column(String)
            the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)
            
            
#        mapper(PGPoint, point_table, properties= {
#                                                  'the_geom' : GeometryColumn(point_table.c.the_geom, comparator=PGComparator)
#                                                  
#                                                  })
        
        
        class PGPoly(Base):
            """The ORM class corresponding to the "poly" table 
            """
            __tablename__ = 'poly'
            gid = Column(Integer, primary_key=True)
            rspdid = Column(Integer) # , primary_key=True) # TODO back to 
            
            # calculated fields
            length = Column(Numeric)                         # the number into this one (calculated by ...)
            number_of_edges = Column(Integer)               # the number of edges (calculated by ...)
            average_edge_length = Column(Numeric)                # the average length of an edge (calculated by ...)
            
            the_geom = GeometryColumn(Geometry(2), 
                                      comparator=PGComparator, 
                                      nullable=True)
            
            # calculated booleans and standard line measures
            no_points = Column(Boolean) 
            is_ring = Column(Boolean)
                    
        class Person(object):
            """The ORM class corresponding to the line in the questionaire
            """
            __tablename__ = 'person'
            id = Column(Integer, primary_key=True)
            
    
    def __call__(self):
        """
        """   
        if  SAVE_AS_SHP:
            self.writePolylineShapeFile()
            
        if SAVE_INTO_POSTGRESQL:
            if CREATE_TABLES:
                self.createTables()
            self.saveToPostresql()
        
        return self.template()
        
    def __init__(self, context, request):
        """
        """
        super(BrowserView, self).__init__(context, request)

    def getValues(self, object):
        return object.getMeasurement()        
 
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
        
    def saveToPostresql(self):
        inref = self.getInRef()
        outref = self.getOutRef()
        transform = osr.CoordinateTransformation(inref, outref)
        
        # let's do the looping
        results = getToolByName(self.context, 'portal_catalog')(portal_type="Measurement")
        gid = 0
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
            
            if cont:   
            
                raw_polyline = self.data_dict.get("polyline",'')
                pairs = raw_polyline.split(";")
                    
                line = ogr.Geometry(type=ogr.wkbLineString)
                
                for pair in pairs:
                
                    coords = pair.split(",")
                    
                    if coords != ['']:
                        
                        x = string.atof(coords[0])
                        y = string.atof(coords[1])
                        
                        line.AddPoint(y, x)
                    
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
                    import pdb;pdb.set_trace()
                    self.session.add(self.PGPoly(gid=gid,
                                                 rspdid= int(r.id ),
                                                 no_points=False,
                                                 the_geom = line.ExportToWkt(),
                                                 length = line.Length(),
                                                 number_of_edges = len(pairs) -1,
                                                 average_edge_length = line.Length() / (len(pairs) -1),
                                                 is_ring = line.IsRing()
                                                 )
                                     )
       
                self.session.commit()
            else:
                print "fluffing out ..."

 
    def writePolylineShapeFile(self):
        
        inref = self.getInRef()
        outref = self.getOutRef()
        
        
        transform = osr.CoordinateTransformation(inref, outref)
        
        
        results = getToolByName(self.context, 'portal_catalog')(portal_type="Measurement")
        
        filename = "/Users/besn/Desktop/results/poly1.shp"
    
        driverName = "ESRI Shapefile"
        drv = ogr.GetDriverByName( driverName )
        drv.DeleteDataSource(filename)
        
        if drv is None:
            print "%s driver not available.\n" % driverName    
        ds = drv.CreateDataSource( filename)
        
        lyr = ds.CreateLayer( "polyline_out", outref, ogr.wkbLineString )
        if lyr is None:
            print "Layer creation failed.\n"
            
        field_defn = ogr.FieldDefn( "rspid", ogr.OFTInteger )
        if lyr.CreateField ( field_defn ) != 0:
            print "Creating Name field failed.\n" 
        
        for r in results:
            
            obj = r.getObject()
            
            values = self.getValues(obj)
            self.data_dict = eval(values)
            
            cont = True
            try:
                int(r.id )
            except:
                cont = False
            if cont:   
            
                raw_polyline = self.data_dict.get("polyline",'')
                
                feat = ogr.Feature( feature_def=lyr.GetLayerDefn())
                
                coord_pairs = raw_polyline.split(";")
                
                coord_pairs = [f.split(",") for f in coord_pairs]
                
                line = ogr.Geometry(type=ogr.wkbLineString)
                
                feat.SetField( "rspid" , int(r.id ))
                
                for p in coord_pairs:
                    
                    try:
                        x = string.atof(p[0])
                        y = string.atof(p[1])
                        
                        line.AddPoint(y, x)
                        print "point added"
                    except:
                        print "something went wrong"
                
                line.AssignSpatialReference(inref)
                line.Transform(transform)
                
                feat.SetGeometryDirectly(line)
                lyr.CreateFeature(feat)
                feat.Destroy()
               
        
  
           
            

        