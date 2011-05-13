from osgeo import ogr

class GraphToShape:
    
    def __init__(self, G):
        self.G = G
        
    def dump(self, filename, original_coverage=None):
        if filename:
            driverName = "ESRI Shapefile"
            drv = ogr.GetDriverByName( driverName )
            drv.DeleteDataSource(filename)
        
            if drv is None:
                print "%s driver not available.\n" % driverName    
            ds = drv.CreateDataSource( filename)
            
            lyr = ds.CreateLayer( "blabla", None, ogr.wkbLineString )
            if lyr is None:
                print "Layer creation failed.\n"
            
            if original_coverage:
                self.originalShapeFile = ogr.Open(original_coverage)
                lyr2 = self.originalShapeFile.GetLayerByIndex(0)
                schema=lyr2.schema
                
                names = []
                for field in schema:
                    if lyr.CreateField(field) != 0:
                        print "Creating Name field failed.\n"
                    else:
                        names.append(field.GetName())
            
            for edge in self.getEdges():
                
                feat = ogr.Feature( feature_def=lyr.GetLayerDefn())
                line = ogr.Geometry(type=ogr.wkbLineString)
                
                for coord in edge.get("geometry").coords:
                    line.AddPoint_2D(coord[0],coord[1])
                
                feat.SetGeometryDirectly(line)
                for name in names:
                    v = edge.get("attributes").get(name)
                    if v:
                        feat.SetField( name, v)
                
                
                lyr.CreateFeature(feat)
                feat.Destroy()
                
            print "Shapefile (%s) written." % filename
                
            
    def getEdges(self):
        edges = self.G.edges()
        nedges = []
        for e in edges:
            edge = self.G.edge[e[0]][e[1]].get("edge")
            nedges.append({'geometry' : edge.getGeometry(),
                           'attributes' : edge.getAttributes()})
        return nedges