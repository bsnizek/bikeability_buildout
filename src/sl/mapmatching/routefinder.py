""" bikeability.dk
    
    (c) 2011 Snizek & Skov-Petersen
    bikeability@life.ku.dk
    http://www.bikeability.dk
    
    License : GPL

    Created on May 9, 2011

    @author: Bernhard Snizek <besn@life.ku.dk>
    @author: Pimin Kostas Kefaloukos
    @author: Hans Skov-Petersen <hsp@life.ku.dk>

    These modules are part of Bikeability.dk.

    Read more about Bikeability her: http://www.bikeability.dk

    Please refer to INSTALL for correct installation as well as information on 
    dependencies etc. 
"""

from label import Label
from random import shuffle
from networkx.algorithms.shortest_paths.generic import shortest_path

BRIDGE_OVERLAP = 10
MAXIMUM_NUMBER_ROUTES = 100
MINIMUM_LENGTH = 0.0
# MAXIMUM_LENGTH = 2000000000000000000000000000.0
DISTANCE_FACTOR = 1.2
NODE_OVERLAP = 1



class RouteFinder():
    
    def __init__(self, graph):
        """
        """
        self.graph = graph
        self.bridges = []
        self.results = []
        self.stack = []
        self.EXPAND_COUNTER = 0
        
#    def expandLabel(self, parentLabel):
#        """
#        """
#        expansion = []   # list of labels
#        newLabel = None  #
#        
#        #out_edges = self.graph.edges(parentLabel.getNode(), self.graph)
#        #out_edges = [e[2].get('edge') for e in out_edges]
#        
#        #print "expanding label at" + str(parentLabel.getNode().getAttributes()) + " " + str(len(out_edges))
#        
##        for edge in out_edges:
##            print edge.getAttributes()
#            
#        print "------"
#        print "Length " ,len(parentLabel.getNode().getOutEdges()) , parentLabel.getNode().getAttributes().get("nodecounter") 
#        for e in parentLabel.getNode().getOutEdges():
#            print "Outedge " , e.getAttributes()
#        
#        for currentEdge in parentLabel.getNode().getOutEdges():
#            # check constraints
#            
#            # import pdb;pdb.set_trace()
#            
#            length = parentLabel.getLength() + currentEdge.getLength()
#            
#            print "currentEdge " + str(currentEdge.getAttributes())
#
#            # newLabel = Label(currentEdge.getToNode(), parent=parentLabel, back_edge=currentEdge, length=length)
#            newLabel = Label(currentEdge.getOutNode(parentLabel), parent=parentLabel, back_edge=currentEdge, length=length)
#                        
#            # path length including this segment longer that MAXIMUM_LENGTH 
#            # constraint
#            if (length > MAXIMUM_LENGTH):
#                print "break (MAXLENGTH)"
#                break
#            
#            print ".."
#            
#            # euclidean distance to endNode > maxLength * distancefactor
#            distanceToEndNode = newLabel.getNode().getGeometry().distance(self.end_node.getGeometry())
#            totalLength = newLabel.getLength() + distanceToEndNode
#            
#            if totalLength > (MAXIMUM_LENGTH * DISTANCE_FACTOR):
#                print "break : euclidian distance greater than max"
#                break
#            
#            nodeOccurances = newLabel.getOccurancesOfNode(newLabel.getNode())
#            
#            if nodeOccurances > NODE_OVERLAP:
#                print "node occurance break (%d) at %s." % (nodeOccurances, str(currentEdge.getAttributes()))
#                break
#            
#            self.num_labels = self.num_labels + 1
#            expansion.append(newLabel)
#            
#        return expansion
    
    def checkNodeOverlap(self, label):
        nc = label.getOccurancesOfNode(label.getNode())
        
        return nc > NODE_OVERLAP
    
    def iterative_expansion(self, label):
        print "Checking Label at " , label.getNode().getAttributes()
        if label.getNode() is self.end_node:
            self.results.append(label)
            return None
        else:
            print "Expanding Label at " , label.getNode().getAttributes()
            labels = self.expandLabel2(label)
            for label2 in labels:
                
                print "Checking node overlap for node ", label2.getNode().getAttributes().get("nodecounter")
                
                if not self.checkNodeOverlap(label2):
                    self.iterative_expansion(label2)
                else:
                    print "--"     
          
#    def expandLabel2(self, parentLabel):
#        """
#        Expands a label and returns the labels of the expanded edges
#        """
#        
#        out_edges = parentLabel.getNode().getOutEdges()
#        for oe in out_edges:
#            print "outEdge " , oe.getAttributes().get("ID_NR")
#            
#        labels =  [Label(edge.getOutNode(parentLabel), 
#                         parent=parentLabel, 
#                         back_edge=edge) for edge in out_edges]
#        return labels
        


        
    def findroutes(self, startNode, endNode):
        
#        sp = shortest_path(self.graph, startNode, endNode)
#        
#        i = 1
#        sum = 0
#        
#        while i < len(sp):
#            edge_by_nodes = (sp[i-1], sp[i])
#            edges = self.graph[edge_by_nodes[0]][edge_by_nodes[1]]
#            # import pdb;pdb.set_trace()
#            if len(edges.keys()) > 1:
#                if edges[0]['edge'].getLength() > edges[1]['edge'].getLength():
#                    sum = sum + edges[1]['edge'].getLength()
#                else:
#                    sum = sum + edges[0]['edge'].getLength()
#            else:
#                sum = sum + edges[0]['edge'].getLength()
#            i = i + 1
#        
#        self.MAXIMUM_LENGTH = sum * DISTANCE_FACTOR
        
        from networkx.algorithms.traversal.depth_first_search import *
        from networkx.algorithms.traversal.breadth_first_search import *
        
        gobject = dfs_labeled_edges(self.graph) # source=startNode)
        
        # gobject = dfs_tree(self.graph, startNode)
    
        #print gobject
        
        #gobject = bfs_predecessors(self.graph, startNode)
        
        # pprint
        
        #pprint.pprint(gobject)        
        
        for x in gobject:
            # print x
            print x[0].getNodeID(), " ", x[1].getNodeID(), " ", x[2].get("dir")
            
        import pdb;pdb.set_trace()
        
        startLabel = Label(startNode, parentLabel=None, parentEdge=None, endNode = endNode, routeFinder = self, length=0, star=startNode.getOutEdges())
        self.expand(startLabel, self.MAXIMUM_LENGTH, MINIMUM_LENGTH, endNode)
        
        return self.results
        

    def getMaxLength(self):
        return self.MAXIMUM_LENGTH

    def expand(self, label, maxLength, minLength, endNode):
        """Expands the label and checks whether the edges are valid
        """
        self.EXPAND_COUNTER += 1
        # print self.EXPAND_COUNTER
        
        edges = label.getStar()
        
        for edge in edges:
            
            to_node = edge.getOutNode(label)
                   
            currentLabel = Label(to_node, 
                                 parentLabel=label, 
                                 parentEdge=edge, 
                                 endNode = endNode, 
                                 routeFinder= self, 
                                 length = edge.getLength(),
                                 star=to_node.getOutEdges())
            
            check = currentLabel.checkValidity(currentLabel)

            print str(check) + " : " + currentLabel.printRouteLabels()

            if check==0:
                # print "endNode reached"
                # print "********"
                # currentLabel.removeEdgeFromStar(edge)
                # print self.EXPAND_COUNTER
                
                self.results.append(currentLabel)
                
            if check==1:
                #print "print expanding"
                self.expand(currentLabel, maxLength, minLength, endNode)
            
            if check==2:
                #print "removing an edge"
                #currentLabel.removeEdgeFromStar(edge)
                #print "CHECK 2"
                pass
            
            if check==3:
                print "MAX LENGTH STOP"    
    
