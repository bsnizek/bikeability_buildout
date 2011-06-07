'''
Created on May 31, 2011

@author: bsnizek
'''
import networkx as nx

class Node:
    
    def __init__(self, id):
        self.id = id
        
class Edge:
    
    def __init__(self, id, node1, node2):
        self.id = id
        self.node1 = node1
        self.node2 = node2


if __name__ == '__main__':
    
    G = nx.Graph()
    
    n0 = Node(id=0)
    n1 = Node(id=1)
    n2 = Node(id=2)
    n3 = Node(id=3)
    n4 = Node(id=4)
    
    e1 = Edge('A', n0, n1)
    e2 = Edge('B', n1, n4)
    e3 = Edge('C', n1, n2)
    e4 = Edge('D', n1, n3)
    
    G.add_edge(n0, n1, {'edge' : e1})
    G.add_edge(n1, n4, {'egge' : e2})
    G.add_edge(n1, n2, {'edge' : e3})
    G.add_edge(n1, n3, {'edge' : e4})
    
    k1 = G[n2].keys()[0]
    print G[n2][k1].get('edge')
    
    
    
    
        