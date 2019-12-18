import osmium as o
import sys
from haversine import haversine, Unit
import os
os.remove('nodes.osm.bz2')
class NodeWriter(o.SimpleHandler):
    def __init__(self,writer):
        o.SimpleHandler.__init__(self)
        self.writer = writer
    def node(self, n):
        if n.tags.get('ref') == None and n.tags.get('railway') == 'stop':
            for i in range(len(RelationHandler.relation_node_dict.keys())):
                if n.id in list(RelationHandler.relation_node_dict.values())[i]:
                    print(list(RelationHandler.relation_node_dict.keys())[i])
                    print(n.tags.get('name'))

        #elif node.ref != None and node.stop == 'stop' and len(node.ref) > 3:
            #print(node.ref)
class RelationHandler(o.SimpleHandler):
    relation_way_dict = {}
    relation_node_dict = {}
    def __init__(self):
        super(RelationHandler, self).__init__()
    def relation(self, w):
        way_id_list = []
        node_id_list = []
        for member in w.members:
            if member.type == 'w' and member.role == '':
                way_id_list.append(member.ref)
            if member.type == 'n':
                #print(member.ref)
                node_id_list.append(member.ref)
                #print(node_id_list)
        #print(w.id)
        RelationHandler.relation_way_dict[w.id] = way_id_list
        RelationHandler.relation_node_dict[w.id] = node_id_list

writer = o.SimpleWriter('nodes.osm.bz2')


R = RelationHandler()
W = NodeWriter(writer)

R.apply_file('export.osm')
W.apply_file('export.osm')