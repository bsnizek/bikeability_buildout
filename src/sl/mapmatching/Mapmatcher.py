'''
Created on May 9, 2011

@author: bsnizek

    install spatialindex from source
    svn co http://svn.gispython.org/spatialindex/spatialindex/trunk
    easy_install RTree
    easy_install PyYAML
    easy_install SIP http://www.riverbankcomputing.com/static/Downloads/sip4/sip-4.12.2.tar.gz
    
    
'''

import networkx as nx
from sl.mapmatching.utils import GraphToShape
try:
    from osgeo import ogr
except ImportError:
    raise ImportError("read_shp() requires OGR: http://www.gdal.org/")
import sys
import shapely.wkt

from routefinder import RouteFinder
from rtree import Rtree
from shapely.geometry import Point

class Edge:
    
    def __init__(self, point2D_from, point2D_to, attributes=None, geometry=None):
        """
        """
        self.from_node = point2D_from
        self.to_node = point2D_to
        self.attributes = attributes
        self.geometry = geometry
        
        sfx1 = self.from_node.getPoint()[0]
        sfx2 = self.to_node.getPoint()[0]
        if sfx1 > sfx2:
            self.minx = sfx2
            self.maxx = sfx1
        else:
            self.minx = sfx1
            self.maxx = sfx2
        sfy1 = self.from_node.getPoint()[1]
        sfy2 = self.to_node.getPoint()[1]
        if sfy1 > sfy2:
            self.miny = sfy2
            self.maxy = sfy1
        else:
            self.miny = sfy1
            self.maxy = sfy2
        
    def getAttributes(self):
        return self.attributes
        
    def getMinX(self):
        return self.minx
        
    
    def getMaxX(self):
        return self.maxx
    
    def getMinY(self):
        return self.miny
    
    def getMaxY(self):
        return self.maxy
    
    def getLength(self):
        return self.geometry.length
    
    def getToNode(self):
        return self.to_node
    
    def getGeometry(self):
        """Returns the edges geometry as a Shapely Multipoint object
        """
        return self.geometry
    
    def setAttributes(self, attributes):
        self.attributes = attributes
        
class Node:
    
    def __init__(self, point, attributes=None):
        
        self.point = point
        self.attributes = attributes
        self.geometry = Point(point[0], point[1])
         
    def getOutEdges(self):
        return [edge.get("edge") for edge in  mm.G[self].values()]
    
    def getPoint(self):
        return self.point
    
    def getAttributes(self):
        return self.attributes
    
    def getGeometry(self):
        return self.geometry
        
class GPSPoint:
    
    def __init__(self, point, attributes):
        self.point = point
        self.attributes = attributes

    def getPoint(self):
        return self.point
    
    def getAttributes(self):
        return self.attributes
    
    def getGeometry(self):
        """Returns the point as a Shapely Point object
        """
        return self.point

class MapMatcher():
    
    def __init__(self):
        self.idx = Rtree()
        self.nodeidx = Rtree()
        self.G = None
        self.edgeindex_edge = {}
        self.edgecounter = 0
        self.nodecounter = 0
        self.gps_points = [];
        self.edge_id__count = {}
        self.node_counter__node = {}
        
        
    def saveGraph(self, filename):
        nx.write_yaml(self.G,filename)
        
    def addNodeToIndex(self, node):
        self.nodeidx.add(self.nodecounter, (node.getPoint()[0], node.getPoint()[1]), obj=node)
        
    
    def addEdgeToIndex(self, edge): 

        self.idx.add(self.edgecounter, (edge.getMinX(), edge.getMinY(), edge.getMaxX(), edge.getMaxY()),obj=edge)
        # print "%d/%d -> %d/%d" % (edge.getMinX(), edge.getMinY(), edge.getMaxX(), edge.getMaxY())
        self.edgeindex_edge[self.edgecounter] = edge
        self.edgecounter = self.edgecounter + 1
        
    def openShape(self, inFile, index=0):
        self.shapeFile = ogr.Open(inFile)
        if self.shapeFile is None:
            print "Failed to open " + inFile + ".\n"
            sys.exit( 1 )
        else:
            print "SHP file successfully read"
     
    def getfieldinfo(self, lyr, feature, flds):
            f = feature
            return [f.GetField(f.GetFieldIndex(x)) for x in flds]
     
    def readGraphFromYAMLFile(self, filename):
        self.G = nx.read_yaml(filename)
        
        
     
    def addlyr(self, G,lyr, fields):
        
        point_coords__nodes = {}
        
        for findex in xrange(lyr.GetFeatureCount()):
            f = lyr.GetFeature(findex)
            flddata = self.getfieldinfo(lyr, f, fields)
            g = f.geometry()
            attributes = dict(zip(fields, flddata))
            attributes["ShpName"] = lyr.GetName()
            if g.GetGeometryType() == 1: #point
                G.add_node((g.GetPoint_2D(0)), attributes)
            if g.GetGeometryType() == 2: #linestring
                last = g.GetPointCount() - 1
                
                p_from = g.GetPoint_2D(0)
                p_to = g.GetPoint_2D(last)
                
                if point_coords__nodes.get(p_from):
                
                    # print "node found"
                    pfrom = point_coords__nodes.get(p_from)  
                
                else:
                    
                    pfrom = Node(p_from, attributes={'from_edge':attributes.get(self.shapeFileUniqueId), "nodecounter":self.nodecounter})
                    self.nodecounter = self.nodecounter + 1 
                    point_coords__nodes[p_from] = pfrom
                
                if point_coords__nodes.get(p_to):
                
                    pto = point_coords__nodes.get(p_to)  
                    # print "node found"    
                
                else:
                
                    pto = Node(p_to, attributes={'to_edge':attributes.get(self.shapeFileUniqueId), "nodecounter":self.nodecounter})
                    self.nodecounter = self.nodecounter + 1 
                    point_coords__nodes[p_to] = pto
                
                shly_geom = shapely.wkt.loads(g.ExportToWkt())
                e = Edge(pfrom, pto, attributes, geometry = shly_geom)
                            
                G.add_edge(pfrom, pto, {"edge": e, "edgecounter" : self.edgecounter})

                # we pull the nodes out of the graph again to index them
                edges_dict = nx.get_edge_attributes(G,"edgecounter")
                
                # import pdb;pdb.set_trace()
                
                edges_keys = edges_dict.keys()
                for k in edges_keys:
                    if self.edgecounter == edges_dict[k]:
                        self.node_counter__node[k[0].getAttributes()['nodecounter']] = k[0]
                        self.node_counter__node[k[1].getAttributes()['nodecounter']] = k[1]
                        self.addNodeToIndex(k[0])
                        self.addNodeToIndex(k[1])
                
                # let us throw the Edge into the index
                self.addEdgeToIndex(e)
                
        return G
            
    def shapeToGraph(self, inFile, uniqueId="FID"):
        # self.G = nx.readwrite.nx_shp.read_shp(inFile)
        
        self.G = nx.DiGraph()
        self.shapeFileUniqueId = uniqueId
        
        lyrcount = self.shapeFile.GetLayerCount() # multiple layers indicate a directory 
        for lyrindex in xrange(lyrcount):
            lyr = self.shapeFile.GetLayerByIndex(lyrindex)
            flds = [x.GetName() for x in lyr.schema]
            self.G=self.addlyr(self.G, lyr, flds)
            
        self.routefinder = RouteFinder(self.G)

    def readGPS(self, inFile):
        self.gpsFile = ogr.Open(inFile)
        if self.gpsFile is None:
            print "Failed to open " + inFile + ".\n"
            sys.exit( 1 )
        else:
            print "GPS file successfully read"
            
            self.shapelyGPS = mm.gpsFile.GetLayer(0)
            
            lyrcount = self.gpsFile.GetLayerCount()
            
            for lyrindex in xrange(lyrcount):
                lyr = self.gpsFile.GetLayerByIndex(lyrindex)
                flds = [x.GetName() for x in lyr.schema]
            
                
            for i in range(self.shapelyGPS.GetFeatureCount()):
                feature = self.shapelyGPS.GetFeature(i)
                geometry = feature.GetGeometryRef()
                
                flddata = self.getfieldinfo(lyr, feature, flds)
                attributes = dict(zip(flds, flddata))
                p = GPSPoint(shapely.wkt.loads(geometry.ExportToWkt()), attributes)
                self.gps_points.append(p)
                
    def maxGPSDistance(self):
        """Calculate the maximum distance of two consecutive GPS Points
        """
        # TODO check whether GPS points are already there
        maxDistance = 0
        gps_point = self.gps_points[0]
        for gpspoint in self.gps_points:
            distance = gpspoint.getGeometry().distance(gps_point.getGeometry())
            gps_point = gps_point
            
            if distance > maxDistance:
                maxDistance = distance
                
        return maxDistance
        

    def nearPoints(self):
        """Sums up the gps point per edge segment. Stores in self.edge_id__count
        """
        # initialize the edge counter
        for edge in self.G.edges():
            self.edge_id__count[self.G[edge[0]][edge[1]].get("edgecounter")] = 0
    
        for point in self.gps_points:
            nearest_edge = self.getNearestEdge(point)
            # print str(point.getAttributes().get("ID")) + "->" + str(nearest_edge.getAttributes().get('Id'))
            self.addPointCountToEdge(nearest_edge)
            
    def addPointCountToEdge(self, edge):
        attributes = edge.getAttributes()
        if self.edge_id__count.has_key(attributes.get(self.shapeFileUniqueId)):
            self.edge_id__count[attributes.get(self.shapeFileUniqueId)] = self.edge_id__count[attributes.get(self.shapeFileUniqueId)] + 1
        else:
            self.edge_id__count[attributes.get(self.shapeFileUniqueId)] = 1
        edge.setAttributes(attributes)
    
    def getNearestEdge(self, point):
        """Returns the edge closes to a Shapely entity given (point) 
        """
        edge = mm.idx.nearest((point.getPoint().x, point.getPoint().y), objects=True)
        edges = [e.object for e in edge]
        if len(edges) == 1:
            result = edges[0]
        else:
            dist = 99999999999999999999999999999999999999999
            for edge in edges:
                distance = point.getPoint().distance(edge.getGeometry())
                if distance < dist:
                    dist = distance
                    result = edge
        return result
    
    
    def getNearestNode(self, point):
        nodes = mm.nodeidx.nearest((point.getPoint().x, point.getPoint().y), objects=True)
        nodes = [n for n in nodes]
        return nodes[0].object
        
    def findRoute(self, returnNonSelection=False):
        
        # pick the start and end GPS points # TODO: sort GPS Points first
        start_point = self.gps_points[0]
        end_point = self.gps_points[-1]
        
        start_node =  self.getNearestNode(start_point)
        end_node =  self.getNearestNode(end_point)
        
        # the start and endnodes returnes by the index are not in the graph, 
        # therefore we need to look them up ....
        
        start_node = self.node_counter__node.get(start_node.getAttributes().get("nodecounter"))
        end_node = self.node_counter__node.get(end_node.getAttributes().get("nodecounter"))
        
        self.routfinder = RouteFinder(self.G)
        label_list = self.routefinder.findroutes(start_node, end_node)

        label_scores = []
        
        # let us loop through the label list 
        for label in label_list:
            number_of_points = 0
            # we sum up the number of points and relate them to the length of the route
            for edge in label.getEdges():
                edge_id = edge.getAttributes().get(self.shapeFileUniqueId)
                number_of_points = number_of_points + self.edge_id__count.get(edge_id)
                
            #we add the scores to a dict
            label_scores.append((label, number_of_points/label.getLength()))
        
        # and extract the maximum score
        score = 0
        selected = None
        
        for ls in label_scores:
            if ls[1] > score:
                selected = ls[0]
                score = ls[1]
        
        if returnNonSelection:
            pass
        else:
            return selected
        
    def eliminiateEmptyEdges(self, distance = 100):
        """Loops through the GPS pointset and selects edges within a boundary of <distance> meters
        """
        print "Edge elimination started"
        
        selected_edge_ids = []
        # let us 
        
        for point in self.gps_points:
            results = self.idx.nearest(((point.getPoint().x-distance/2), 
                                     (point.getPoint().y-distance/2),
                                     (point.getPoint().x+distance/2),
                                     (point.getPoint().y+distance/2)), objects=True)
            for result in results:
                from_node = self.node_counter__node.get(result.object.from_node.getAttributes().get("nodecounter"))
                to_node = self.node_counter__node.get(result.object.to_node.getAttributes().get("nodecounter"))
                edge_counter = self.G.edge[from_node][to_node].get("edgecounter")
                if edge_counter not in selected_edge_ids:
                    selected_edge_ids.append(edge_counter)
        print str(len(selected_edge_ids)) + " edges found to keep."
        
        elimination_counter = 0
        for edge in self.G.edges():
            edgecounter = self.G.edge[edge[0]][edge[1]].get("edgecounter")
            if edgecounter not in selected_edge_ids:
                edge_tuple = (self.G.edge[edge[0]][edge[1]].get("edge").from_node, self.G.edge[edge[0]][edge[1]].get("edge").to_node)
                self.G.remove_edge(*edge_tuple)
                elimination_counter =  elimination_counter + 1
          
        print str(elimination_counter) + " edges eliminated."
        

if __name__ == '__main__':
    
    NETWORK_ELIMINATION = False

    mm = MapMatcher()
    mm.openShape("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/SparseNetwork.shp")
    
    print "Road network imported"
    
    print "Parsing road network -> graph"
    mm.shapeToGraph("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/SparseNetwork.shp", uniqueId="ID_NR")
    print "Graph generated"
    
    #mm.saveGraph("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/Network.yaml")
    #print "Graph saved"
    
    mm.readGPS("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/GPS_Points.shp")
    
    # max_distance = mm.maxGPSDistance()

    if NETWORK_ELIMINATION:    
        max_distance = 300

        print "The maximum distance between 2 adjacent GPS points is %d" % max_distance
        mm.eliminiateEmptyEdges(distance = max_distance + 0.5)
    
        gts = GraphToShape(mm.G)
        gts.dump("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/SparseNetwork.shp",
                 original_coverage = "/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/Network.shp")    
    
    mm.nearPoints()
    print "Near points executed"

    selected_label = mm.findRoute(returnNonSelection=False)

    print selected_label

    if selected_label:

        if (type(selected_label) == tuple):
            selected_label[0].saveAsShapeFile("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/SelectedRoute.shp")
            non_selected_counter = 0
            for non_selected in selected_label[1]:
                non_selected.saveAsShapeFile("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/Nonselected-" + non_selected_counter + ".shp")
                non_selected_counter = non_selected_counter + 1 
        else:
            selected_label.saveAsShapeFile("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/SelectedRoute.shp")
    else:
        print "No route found"
        
    print "Finished"