""" bikeability.dk
    
    (c) 2011 Snizek & Skov-Petersen
    bikeability@life.ku.dk
    http://www.bikeability.dk
    
    License : GPL
"""

from label import Label

BRIDGE_OVERLAP = 10
MAXIMUM_NUMBER_ROUTES = 20
MINIMUM_LENGTH = 100
MAXIMUM_LENGTH = 2000000000000000000000000000
DISTANCE_FACTOR = 2
NODE_OVERLAP = 2


class RouteFinder():
    
    def __init__(self, graph):
        """
        """
        self.graph = graph
        self.bridges = []
        
        
    def expandLabel(self, parentLabel):
        """
        """
        expansion = []   # list of labels
        newLabel = None  #
        end_node = None
        
        out_edges = self.graph.edges(parentLabel.getNode(), self.graph)
        out_edges = [e[2].get('edge') for e in out_edges]
        
        # import pdb;pdb.set_trace()
        
        for currentEdge in parentLabel.getNode().getOutEdges():
            # check constraints
            
            length = parentLabel.getLength() + currentEdge.getLength()
            
            newLabel = Label(currentEdge.getToNode(), parent=parentLabel, back_edge=currentEdge, length=length)
            
            edgeOccurances = newLabel.getOccurancesOfEdge(newLabel)
            
            isInBridges = True
            try:
                self.bridges.index(newLabel)
            except ValueError:
                isInBridges = False
            
            if (isInBridges) and edgeOccurances > BRIDGE_OVERLAP:
                print "break (isInBridges)"
                break
            
            # path length including this segment longer that MAXIMUM_LENGTH 
            # constraint
            if (length > MAXIMUM_LENGTH):
                print "break (MAXLENGTH)"
                break
            
            # euclidean distance to endNode > maxLength * distancefactor
            distanceToEndNode = newLabel.getNode().getGeometry().distance(self.end_node.getGeometry())
            totalLength = newLabel.getLength() + distanceToEndNode
            if totalLength > (MAXIMUM_LENGTH * DISTANCE_FACTOR):
                print "break : euclidean"
                break
            
            nodeOccurances = newLabel.getOccurancesOfNode(newLabel.getNode())
            
            if nodeOccurances > NODE_OVERLAP:
                print "node occurance break (%d)" % len(nodeOccurances)
                break
            
            self.num_labels = self.num_labels + 1
            expansion.append(newLabel)
            
        return expansion
            
    def findroutes(self, start_node, end_node):
        self.num_labels = 0
        self.result = []
        self.start_node = start_node
        self.end_node = end_node
        
        stack = [Label(self.start_node)]
        
        while (len(stack) != 0):
            
            expandingLabel = stack.pop()
            
            expansion = self.expandLabel(expandingLabel)
        
            for currentLabel in expansion:
        
                if (self.isValidRoute(currentLabel)):
                    self.result.append(currentLabel)
                    
                    if len(self.result) >= MAXIMUM_NUMBER_ROUTES:
                        return self.result
                
                stack.append(currentLabel)
                
        return self.result
                
    def isValidRoute(self, label):
        return label.getNode() == self.end_node and label.getLength() >= MINIMUM_LENGTH and label.getLength() <= MAXIMUM_LENGTH
    
    
