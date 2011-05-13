from osgeo import ogr

class Label:
    
    def __init__(self, node, parent=None, back_edge=None, length=0):
        self.node = node
        self.parent = parent
        self.back_edge = back_edge
        self.length = length
        
    def getParent(self):
        return self.parent
    
    def getNode(self):
        return self.node
    
    def getBackEdge(self):
        return self.back_edge
    
    def getLength(self):
        return self.length
    
    def getOccurancesOfEdge(self, edge):
        label = self
        result = 0
        while (label.getBackEdge() != None ):
            backedge = label.getBackEdge()
            if (edge == backedge):
                result = result + 1
            label = label.getParent()
            
        return result
    
    def getOccurancesOfNode(self, node):
        """
        """
        label = self
        result = []
        while (label != None):
            result.append(label.getBackEdge())
            label = label.getParent()
            
        result.reverse()
        return result
    
    def getRouteLabels(self):
        """Returns the route as labels
        """
        labels = []
        currlabel = self
        # labels.append(self)
        
        while currlabel:
            currlabel = currlabel.getParent()
            labels.append(currlabel)

        return  [self] + labels
    
    def getEdges(self):
        edges = [label.getBackEdge() for label in self.getRouteLabels() if label]
        edges = [edge for edge in edges if edge]
        edges.reverse()
        return edges
    
    def getRouteAttributes(self):
        
        return [edge.getAttributes() for edge in self.getEdges()] 
    
    def printRouteAttributes(self):
        print [edge.getAttributes() for edge in self.getEdges()] 
        
        
    def saveAsShapeFile(self, filename=None):
        """Saves the route as a Shapefile
        """
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
            
            
            
            for edge in self.getEdges():
                feat = ogr.Feature( feature_def=lyr.GetLayerDefn())
                line = ogr.Geometry(type=ogr.wkbLineString)
                wkb = edge.getGeometry().to_wkb()
                for coord in edge.getGeometry().coords:
                    line.AddPoint_2D(coord[0],coord[1])
                feat.SetGeometryDirectly(line)
                lyr.CreateFeature(feat)
                feat.Destroy()
    
        
        
        