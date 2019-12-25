import osmium as o
import sys
from haversine import haversine, Unit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from io import StringIO, BytesIO
def returndistance_dict():

    station_count = {'G':19, 'M':25, 'H':21, 'C':20, 'Y':24, 'Z':14, 'N':19, 'F':16, 'A':20, 'I':27, 'S':21}

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
            RelationHandler.relation_way_dict[w.tags.get('ref')] = way_id_list
            RelationHandler.relation_node_dict[w.tags.get('ref')] = node_id_list

    class Node:
        def __init__(self, id, name, location, ref, isTransferStation, stop):
            self.id = id
            self.name = name
            self.location = location
            self.ref = ref
            self.isTransferStation = isTransferStation
            self.stop = stop
    
        def get_start_end(self,relation_ref):
            self.start = relation_ref + '01'
            self.end = relation_ref + station_count[relation_ref]

    all_node_list = []
    class NodeHandler(o.SimpleHandler):
        newlist = []
        def __init__(self):
            super(NodeHandler, self).__init__()
        def node(self, w):
            #if w.tags.get('ref') == None and w.tags.get('name') != None:
                #print(w.tags.get('name'))
            #if w.tags.get('ref') != None:
            all_node_list.append(Node(w.id, w.tags.get('name'), w.location, w.tags.get('ref'), False, w.tags.get('public_transport')))

    class WayHandler(o.SimpleHandler):
        all_way_dict = {}
        def __init__(self):
            super(WayHandler, self).__init__()
        def way(self, w):
            node_id_list = []
            for node in w.nodes:
                node_id_list.append(node.ref)
            WayHandler.all_way_dict[w.id] = node_id_list

    class Relation_way:
        def __init__(self,id,big_list):
            self.id = id
            self.big_list = big_list    

    idx = o.index.create_map("sparse_file_array")
    R = RelationHandler()
    G = WayHandler()
    H = NodeHandler()

    R.apply_file('export_new.osm')
    G.apply_file('export_new.osm')
    H.apply_file('export_new.osm')

    # split station with multiple reference
    def ref_split(node):
        '''
        input: class object Node
        output: None, change class object Node's reference to its belongings
        '''
        if ';' in str(node.ref):
            ref_list = node.ref.split(';')
            node.ref = []
            for rel_id in RelationHandler.relation_node_dict.keys():
                if node.id in RelationHandler.relation_node_dict[rel_id]:
                    for ref in ref_list:
                        if str(rel_id) in ref:
                            node.ref.append(ref)
            if len(node.ref) == 1 :
                node.ref = ''.join(node.ref)
                #print(node.ref)
            else :
                node.ref = ';'.join(node.ref)
                #print(node.ref)


    for node in all_node_list:
        ref_split(node)

    for node in all_node_list:
        for relation_keys in RelationHandler.relation_node_dict.keys():
            if node in RelationHandler.relation_node_dict[relation_keys]:
                node.get_start_end(relation_keys)

    for x,y in zip(range(0,len(all_node_list)-1),range(1,len(all_node_list))):
        if all_node_list[x].name == all_node_list[y].name:
            all_node_list[x].isTransferStation = True
            all_node_list[y].isTransferStation = True


    node_class_dict = {}
    for relation_keys in RelationHandler.relation_node_dict.keys():
        node_class_dict[relation_keys] = []
    for node in all_node_list:
        for relation_keys in RelationHandler.relation_node_dict.keys():
            if node.id in RelationHandler.relation_node_dict[relation_keys] and (node.stop == 'station' or node.stop == 'stop_position'):
                node_class_dict[relation_keys].append(node)
                            



    all_way_list = []
    for key in RelationHandler.relation_way_dict.keys():
        way_list =[]
        for way_id in WayHandler.all_way_dict.keys():
            if way_id in RelationHandler.relation_way_dict[key]:
                way_list.append(WayHandler.all_way_dict[way_id])
        all_way_list.append(Relation_way(key,way_list))


    #print(all_way_list[0].id)

    def ReturnWay(Node1,Node2):
        '''
        input : Two nodes station that are next to each other
        output : a list of nodes that connect two stations
        '''

        count = 0
        for relation_ref in RelationHandler.relation_node_dict.keys():
            if Node1 in RelationHandler.relation_node_dict[relation_ref] and Node2 in RelationHandler.relation_node_dict[relation_ref]:
                way_in_relation = RelationHandler.relation_way_dict[relation_ref][:]

        way_in_relation = list(map(lambda x : WayHandler.all_way_dict[x], way_in_relation))

        for way in way_in_relation:
            if Node1 in way:
                node1_way = way[:]
                way_index = way_in_relation.index(way)

        skip_index_list = [way_index]
        while 0 <= count < len(way_in_relation[:]):
            if count in skip_index_list:
                count += 1
                continue
            if Node2 in node1_way:
                break
            if node1_way[0] == way_in_relation[count][0]:
                node1_way.pop(0)
                node1_way = way_in_relation[count][::-1] + node1_way
                skip_index_list.append(count)
                count = 0
                continue
            if node1_way[0] == way_in_relation[count][-1]:
                node1_way.pop(0)
                node1_way = way_in_relation[count] + node1_way
                skip_index_list.append(count)
                count = 0
                continue
            if node1_way[-1] == way_in_relation[count][0]:
                node1_way.pop()
                node1_way += way_in_relation[count]
                skip_index_list.append(count)
                count = 0
                continue
            if node1_way[-1] == way_in_relation[count][-1]:
                node1_way.pop()
                node1_way += way_in_relation[count][::-1]
                skip_index_list.append(count)
                count = 0
                continue
            count += 1

        if node1_way.index(Node1) > node1_way.index(Node2):
            node1_way = node1_way[node1_way.index(Node2):node1_way.index(Node1)+1]
        else:
            node1_way = node1_way[node1_way.index(Node1):node1_way.index(Node2)+1]
        
        return node1_way

    def countWaydistance(way):
        '''
        input : a list of node_id
        output : sum of distance between neighbor nodes
        '''
        geometry_list = []
        distance = 0
        for node_id in way:
            for node in all_node_list:
                if node.id == node_id:
                    geometry_list.append((node.location.lat,node.location.lon))
        for i,j in zip(range(len(geometry_list)),range(1,len(geometry_list))):
            distance += haversine(geometry_list[i], geometry_list[j], unit = 'm')
        return distance

    def get_node_id(node_ref):
        '''
        input : node reference (ex:G04, H03)
        output : node id
        '''
        for node in all_node_list:
            if node.ref != None:
                if node_ref in node.ref:
                    return node.id
    def get_node_ref(node_id):
        '''
        input : node reference (ex:G04, H03)
        output : node id
        '''
        for node in all_node_list:
            if node.id == node_id:
                return node.ref

    def get_node_type(node_id):
        '''
        input : node id
        output : node type switch boolean
        '''
        for node in all_node_list:
            if node.id == node_id:
                if node.stop == 'switch':
                    return False


    del_way_list =[]
    for way in WayHandler.all_way_dict.keys():
        #print(get_node_type(WayHandler.all_way_dict[way][0]))
        if get_node_type(WayHandler.all_way_dict[way][0]) == True and get_node_type(WayHandler.all_way_dict[way][-1]) == True:
            del_way_list.append(way)

    for way in del_way_list:
        del WayHandler.all_way_dict[way]


    get_ref_node_list =[]
    # find station without reference
    for node in all_node_list:
        if node.ref == None and node.stop == 'stop_position':
            get_ref_node_list.append(node.name)
    #print(len(get_ref_node_list))
    get_ref_node_list = list(set(get_ref_node_list))
    #print(get_ref_node_list)




    

    station_ref = {}
    for relation in station_count.keys():
        temp_list = []
        for i in range(station_count[relation]):
            temp_list.append(relation + str(i+1).zfill(2))
            station_ref[relation] = temp_list


    distance = {}

    ref_miss_count = 0

    for relation in station_count.keys():
        temp_list = []
        for i,j in zip(range(len(station_ref[relation])-1),range(1,len(station_ref[relation]))):
            try:
                temp_list.append(countWaydistance(ReturnWay(get_node_id(station_ref[relation][i]),get_node_id(station_ref[relation][j]))))
            except ValueError:
                #print(station_ref[relation][i],station_ref[relation][j])
                temp_list.append(None)
                pass
            except UnboundLocalError:
                #print(station_ref[relation][i],station_ref[relation][j])
                temp_list.append(None)
                #ref_miss_count += 1
        distance[relation] = temp_list


    for distance_list in distance.values():
        for i in range(len(distance_list)):
            if distance_list[i] != None:
                distance_list[i] = distance_list[i] / 12


    return distance


def get_ref_from_name(name):

    class Node:
        def __init__(self, id, name, location, ref, isTransferStation, stop):
            self.id = id
            self.name = name
            self.location = location
            self.ref = ref
            self.isTransferStation = isTransferStation
            self.stop = stop
 
    all_node_list = []

    class NodeHandler(o.SimpleHandler):
        newlist = []
        def __init__(self):
            super(NodeHandler, self).__init__()
        def node(self, w):
            #if w.tags.get('ref') == None and w.tags.get('name') != None:
                #print(w.tags.get('name'))
            #if w.tags.get('ref') != None:
            all_node_list.append(Node(w.id, w.tags.get('name'), w.location, w.tags.get('ref'), False, w.tags.get('public_transport')))

    N = NodeHandler()
    N.apply_file('export_new.osm')


    temp_ref_list =[]
    for node in all_node_list:
        if node.stop == 'stop_position':
            if name in node.name:
                temp_ref_list.append(node.ref)

    return temp_ref_list


def return_node_dict():
    
    station_count = {'G':19, 'M':25, 'H':21, 'C':20, 'Y':24, 'Z':14, 'N':19, 'F':16, 'A':20, 'I':27, 'S':21}

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
            RelationHandler.relation_way_dict[w.tags.get('ref')] = way_id_list
            RelationHandler.relation_node_dict[w.tags.get('ref')] = node_id_list

    class Node:
        def __init__(self, id, name, location, ref, isTransferStation, stop, index=None):
            self.id = id
            self.name = name
            self.location = location
            self.ref = ref
            self.isTransferStation = isTransferStation
            self.stop = stop
            self.index = index
    
        def get_start_end(self,relation_ref):
            self.start = relation_ref + '01'
            self.end = relation_ref + station_count[relation_ref]

        def __str__(self):
            return self.ref

    all_node_list = []
    class NodeHandler(o.SimpleHandler):
        newlist = []
        def __init__(self):
            super(NodeHandler, self).__init__()
        def node(self, w):
            #if w.tags.get('ref') == None and w.tags.get('name') != None:
                #print(w.tags.get('name'))
            #if w.tags.get('ref') != None:
            all_node_list.append(Node(w.id, w.tags.get('name'), w.location, w.tags.get('ref'), False, w.tags.get('public_transport')))

    class WayHandler(o.SimpleHandler):
        all_way_dict = {}
        def __init__(self):
            super(WayHandler, self).__init__()
        def way(self, w):
            node_id_list = []
            for node in w.nodes:
                node_id_list.append(node.ref)
            WayHandler.all_way_dict[w.id] = node_id_list

    class Relation_way:
        def __init__(self,id,big_list):
            self.id = id
            self.big_list = big_list    

    idx = o.index.create_map("sparse_file_array")
    R = RelationHandler()
    G = WayHandler()
    H = NodeHandler()

    R.apply_file('export_new.osm')
    G.apply_file('export_new.osm')
    H.apply_file('export_new.osm')

    # split station with multiple reference
    def ref_split(node):
        '''
        input: class object Node
        output: None, change class object Node's reference to its belongings
        '''
        if ';' in str(node.ref):
            ref_list = node.ref.split(';')
            node.ref = []
            for rel_id in RelationHandler.relation_node_dict.keys():
                if node.id in RelationHandler.relation_node_dict[rel_id]:
                    for ref in ref_list:
                        if str(rel_id) in ref:
                            node.ref.append(ref)
            if len(node.ref) == 1 :
                node.ref = ''.join(node.ref)
                #print(node.ref)
            else :
                node.ref = ';'.join(node.ref)
                #print(node.ref)


    for node in all_node_list:
        ref_split(node)

    for node in all_node_list:
        for relation_keys in RelationHandler.relation_node_dict.keys():
            if node in RelationHandler.relation_node_dict[relation_keys]:
                node.get_start_end(relation_keys)

    for x,y in zip(range(0,len(all_node_list)-1),range(1,len(all_node_list))):
        if all_node_list[x].name == all_node_list[y].name:
            all_node_list[x].isTransferStation = True
            all_node_list[y].isTransferStation = True


    node_class_dict = {}
    for relation_keys in RelationHandler.relation_node_dict.keys():
        node_class_dict[relation_keys] = []
    for node in all_node_list:
        for relation_keys in RelationHandler.relation_node_dict.keys():
            if node.id in RelationHandler.relation_node_dict[relation_keys] and (node.stop == 'station' or node.stop == 'stop_position'):
                node_class_dict[relation_keys].append(node)

    return node_class_dict

if __name__ == "__main__":
    print(returndistance_dict())
    print(get_ref_from_name('新宿'))
    print(return_node_dict())
    print(returndistance_dict.countWaydistance([get_node_id('G04'), get_node_id('G09')]))