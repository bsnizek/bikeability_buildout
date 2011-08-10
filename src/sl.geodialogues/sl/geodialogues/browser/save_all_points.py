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

from Products.Five import BrowserView
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.component.hooks import getSite
import transaction
from DateTime import DateTime
from random import random
from Products.CMFPlone.utils import _createObjectByType
import sys
from osgeo import ogr,osr
import string
from Products.CMFCore.utils import getToolByName
import pprint
from config import PROJECTION


class SaveAllPoints(BrowserView):
    """
    """
    
    template = ViewPageTemplateFile('templates/save_shp_file.pt')
    
    def __call__(self):
        """
        """    
        # self.writePolylineShapeFile()
        self.writePointShapeFile();
        return self.template()
        
    def __init__(self, context, request):
        """
        """
        
        super(BrowserView, self).__init__(context, request)
    
    def getValues(self, object):
        return object.getMeasurement()
        
    def getGoodText0(self, object):
        return self.data_dict.get("good-text0","")
    
    
    def getGoodText1(self):
        return self.data_dict.get("good-text1","")
    
    def getGoodText2(self):
        return self.data_dict.get("good-text2","")
    
    def getGoodDrop0(self):
        return self.data_dict.get("good-drop0","")
    
    def getGoodDrop1(self):
        return self.data_dict.get("good-drop1","")
    
    def getGoodDrop2(self):
        return self.data_dict.get("good-drop2","")
    
    def getGoodCoord0(self):
        return self.data_dict.get("good-coord0","")

    def getGoodCoord1(self):
        return self.data_dict.get("good-coord1","")
    
    def getGoodCoord2(self):
        return self.data_dict.get("good-coord2","")
    
    
    
    def getCoord(self, n=0, type="good"):
        return self.data_dict.get("%s-coord%d" % (type,n),"")
    
    def getText(self, n=0, type="good"):
        return self.data_dict.get("%s-text%d" % (type,n),"")
    
    def getDrop(self, n=0, type="good"):    
        return self.data_dict.get("%s-drop%d" % (type,n),"")
    
           
        
    def writePointShapeFile(self):
        
        inref = osr.SpatialReference()
        inref.ImportFromEPSG(4326)
        
        outref = osr.SpatialReference()
        # outref.SetFromUserInput("EPSG:25832")                                    # GCS_WGS_1984
        outref.ImportFromProj4("+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs") # ETRS_1989_UTM_Zone_32N
        
        
        transform = osr.CoordinateTransformation(inref, outref)
        
        driverName = "ESRI Shapefile"
        drv = ogr.GetDriverByName( driverName )
        if drv is None:
            print "%s driver not available.\n" % driverName
        
        # % self.context.id 
        
        filename = "/Users/besn/Desktop/results/points.shp" 
        drv.DeleteDataSource(filename)
            
        ds = drv.CreateDataSource( filename)
        if ds is None:
            print "Creation of output file failed.\n"
            return None

        lyr = ds.CreateLayer( "point_out", outref, ogr.wkbPoint )
        if lyr is None:
            print "Layer creation failed.\n"
            sys.exit( 1 )
        
        field_defn = ogr.FieldDefn( "rspid", ogr.OFTInteger )
        if lyr.CreateField ( field_defn ) != 0:
            print "Creating Name field failed.\n"  
        
        
        field_defn = ogr.FieldDefn( "type", ogr.OFTString )
        field_defn.SetWidth( 4)
        if lyr.CreateField ( field_defn ) != 0:
            print "Creating Name field failed.\n"

        field_defn = ogr.FieldDefn( "t_nmbr", ogr.OFTInteger )
        if lyr.CreateField ( field_defn ) != 0:
            print "Creating Name field failed.\n"

        field_defn = ogr.FieldDefn( "text", ogr.OFTString )
        field_defn.SetWidth( 128 )
        if lyr.CreateField ( field_defn ) != 0:
            print "Creating Name field failed.\n"            

        field_defn = ogr.FieldDefn( "dropdown", ogr.OFTString )
        field_defn.SetWidth( 32 )
        if lyr.CreateField ( field_defn ) != 0:
            print "Creating Name field failed.\n"

        
        results = getToolByName(self.context, 'portal_catalog')(portal_type="Measurement")

        points_filename = "/Users/besn/Desktop/results/points.shp"
        poly_lyr = ogr.Open(points_filename)
    
        for r in results:
            obj = r.getObject()
    
            values = self.getValues(obj)
            self.data_dict = eval(values)

            pprint.pprint(self.data_dict)

            for type in ["good","bad"]:
                for n in [0,1,2]:
                    coords = self.getCoord(n=n, type=type)
                    if coords != '':
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
                            pt = ogr.Geometry(ogr.wkbPoint)
                            feat = ogr.Feature( lyr.GetLayerDefn())
                            
                            text = self.getText(n=n, type=type)
                            drop = self.getDrop(n=n, type=type)
                            
                            feat.SetField( "rspid" , int(r.id ))
                            feat.SetField( "type" , type )
                            feat.SetField("t_nmbr", n)
                            feat.SetField( "text" , text)
                            feat.SetField( "dropdown", drop)
                            
                            
                            text = self.getText(n=n, type=type)
                            drop = self.getDrop(n=n, type=type)
                            
                            
                            pt.SetPoint_2D(0, y, x)
                            pt.AssignSpatialReference(inref)
                            pt.Transform(transform)
                            feat.SetGeometryDirectly(pt)
                            
                            
                            # let us calculate the distance to the polyline
                            # exe2 = poly_lyr.ExecuteSQL("SELECT * from poly1 WHERE 'rspid'=" + r.id)
                            # pl_feature = exe2[0]
                            # pl_geom = pl_feature.GetGeometryRef()
                            

                            lyr.CreateFeature(feat) 
                            feat.Destroy()
           
            

        