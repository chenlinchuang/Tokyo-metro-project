import osmium as o
import sys
class RelationHandler(o.SimpleHandler):
    relation_way_list =[]
    def __init__(self):
        super(RelationHandler, self).__init__()

    def relation(self, w):
        way_id_list = []
        node_id_list = []
        for member in w.members:
            if member.type == 'w' and member.role == '':
                way_id_list.append(member.ref)
            if member.type == 'n':
                node_id_list.append(member.ref)
        RelationHandler.relation_way_list.append(node_id_list)

class Node:
    def __init__(self, id, name, ref, isTransferStation):
        self.id = id
        self.name = name
        self.ref = ref
        self.isTransferStation = isTransferStation
all_node_list = []

class NodeHandler(o.SimpleHandler):
    newlist = []
    def __init__(self):
        super(NodeHandler, self).__init__()
    def node(self, w):
        if w.tags.get('ref') == None and w.tags.get('name') != None:
            print(w.tags.get('name'))
        if w.tags.get('ref') != None:
            if len(w.tags.get('ref')) > 5:
                all_node_list.append(Node(w.id, w.tags.get('name'), w.tags.get('ref'), True))
            else:
                all_node_list.append(Node(w.id, w.tags.get('name'), w.tags.get('ref'), False))


class WayHandler(o.SimpleHandler):

    def __init__(self):
        super(WayHandler, self).__init__()

    def way(self, w):
        pass
        #print(w.nodes)
        #print("%d %s" %(w.id, len(w.nodes)))


idx = o.index.create_map("sparse_file_array")
G = WayHandler()

R = RelationHandler()
H = NodeHandler()
G.apply_file('export.osm')
H.apply_file('export.osm')
R.apply_file('export.osm')

for x,y in zip(range(0,len(all_node_list)-1),range(1,len(all_node_list))):
    if all_node_list[x].name == all_node_list[y].name:
        all_node_list[x].isTransferStation = True
        all_node_list[y].isTransferStation = True

#for node in all_node_list:
    #if node.isTransferStation == True:
        #print(node.ref)