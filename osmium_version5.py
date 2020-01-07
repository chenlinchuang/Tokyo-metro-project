import osmium as o
import sys
from haversine import haversine, Unit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from io import StringIO, BytesIO
import operator
import random
import csv
import requests
from bs4 import BeautifulSoup

def count_way_distance(ref1,ref2):
    
    station_count = {'G':19, 'M':25, 'H':21, 'C':20, 'T':23, 'E':38, 'Y':24, 'Z':14, 'N':19, 'F':16, 'A':20, 'I':27, 'S':21}

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

    def get_node_id(node_ref):
        '''
        input : node reference (ex:G04, H03)
        output : node id
        '''
        for node in all_node_list:
            if node.ref != None:
                if node_ref in node.ref:
                    return node.id

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

        '''
        input : a list of node_id
        output : sum of distance between neighbor nodes
        '''
    def countwaydistance(way):
        geometry_list = []
        distance = 0
        for node_id in way:
            for node in all_node_list:
                if node.id == node_id:
                    geometry_list.append((node.location.lat,node.location.lon))
        for i,j in zip(range(len(geometry_list)),range(1,len(geometry_list))):
            distance += haversine(geometry_list[i], geometry_list[j], unit = 'm')
        return distance

    return countwaydistance(ReturnWay(get_node_id(ref1),get_node_id(ref2)))



def returndistance_dict():

    line = ['A', 'I', 'S', 'E', 'G', 'M', 'H', 'T', 'C', 'Y', 'Z', 'N', 'F']
    URL_list = ['https://zh.wikipedia.org/wiki/%E6%B7%BA%E8%8D%89%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E4%B8%89%E7%94%B0%E7%B7%9A_(%E9%83%BD%E7%87%9F%E5%9C%B0%E4%B8%8B%E9%90%B5)',
                'https://zh.wikipedia.org/wiki/%E6%96%B0%E5%AE%BF%E7%B7%9A_(%E9%83%BD%E7%87%9F%E5%9C%B0%E4%B8%8B%E9%90%B5)',
                'https://zh.wikipedia.org/wiki/%E5%A4%A7%E6%B1%9F%E6%88%B6%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E9%8A%80%E5%BA%A7%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E4%B8%B8%E4%B9%8B%E5%85%A7%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E6%97%A5%E6%AF%94%E8%B0%B7%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E6%9D%B1%E8%A5%BF%E7%B7%9A_(%E6%9D%B1%E4%BA%AC%E5%9C%B0%E4%B8%8B%E9%90%B5)',
                'https://zh.wikipedia.org/wiki/%E5%8D%83%E4%BB%A3%E7%94%B0%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E6%9C%89%E6%A8%82%E7%94%BA%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E5%8D%8A%E8%97%8F%E9%96%80%E7%B7%9A',
                'https://zh.wikipedia.org/wiki/%E5%8D%97%E5%8C%97%E7%B7%9A_(%E6%9D%B1%E4%BA%AC%E5%9C%B0%E4%B8%8B%E9%90%B5)',
                'https://zh.wikipedia.org/wiki/%E5%89%AF%E9%83%BD%E5%BF%83%E7%B7%9A'
                ]
    missing_line = {}

    for i in range(len(URL_list)):
        temp_list =[]
        res = requests.get(URL_list[i]).text
        soup = BeautifulSoup(res,'lxml')
        for items in soup.find('table', class_='wikitable').find_all('tr')[1::]:
            #print(len(items))
            if len(items) <=8:
                continue
            data = items.find_all(['td','th'])
            #print(data)
            if i == len(URL_list) -2 :
                temp_list.append(data[5].text.strip())
            else:
                temp_list.append(data[4].text.strip())
        missing_line[line[i]] = temp_list

    for value in missing_line.values():
        del value[0]


    station_count = {'G':19, 'M':25, 'H':21, 'C':20, 'T':23, 'E':38, 'Y':24, 'Z':14, 'N':19, 'F':16, 'A':20, 'I':27, 'S':21}

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
                temp_list.append(0)
                pass
            except UnboundLocalError:
                #print(station_ref[relation][i],station_ref[relation][j])
                temp_list.append(0)
                #ref_miss_count += 1
        distance[relation] = temp_list

    for distance_list in distance.values():
        for i in range(len(distance_list)):
            distance_list[i] = distance_list[i] / 12

    station_count = {'G':19, 'M':25, 'H':21, 'T':23, 'C':20, 'Y':24, 'Z':14, 'N':19, 'F':16, 'E':38, 'S':21, 'I':27, 'A':20}

    for key in distance.keys():
        for i in range(len(distance[key])):
            if distance[key][i] == 0 or distance[key][i] >= 2000:
                try:
                    distance[key][i] = int(float(missing_line[key][i]) * 80)
                except KeyError:
                    print(missing_line[key],distance[key][i])
    for value in distance.values():
        for i in range(len(value)):
            value[i] = int(value[i])
    with open('lines.csv','w+',newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter = ';')
        for relation in station_count.keys():
            writerow = [relation,'01',station_count[relation]]
            writerow.extend([round(x/60, 2) for x in distance[relation]])
            writer.writerow(writerow)
    
    
    return distance


def get_ref_from_name(name):

    if '駅' in name:
        ind = name.index('駅')
        name = name[:ind]
    line_T = {'中野':['T01'],'落合':['T02'], '高田馬場':['T03'], '早稲田':['T04'], '神楽坂':['T05'], '飯田橋':['T06'],
              '九段下':['T07'], '竹橋':['T08'], '大手町':['T09'], '日本橋':['T10'], '茅場町':['T11'], '門前仲町':['T12'],
              '木場':['T13'], '東陽町':['T14'], '南砂町':['T15'], '西葛西':['T16'], '葛西':['T17'], '浦安':['T18'],
              '南行徳':['T19'], '行徳':['T20'], '妙典':['T21'], '原木中山':['T22'], '西船橋':['T23']}
    if name in line_T.keys():
         return line_T[name]

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
        if node.stop == 'stop_position' or 'station':
            try:
                if name in node.name:
                    temp_ref_list.append(node.ref)
            except TypeError:
                pass
    return temp_ref_list


def return_node_dict():
    

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
        def __init__(self, id, name, location, ref, isTransferStation, stop, index=None, wiki_data=None):
            self.id = id
            self.name = name
            self.location = location
            self.ref = ref
            self.isTransferStation = isTransferStation
            self.stop = stop
            self.index = index
            self.wiki = wiki_data
    
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
            all_node_list.append(Node(w.id, w.tags.get('name'), w.location, w.tags.get('ref'), False, w.tags.get('public_transport')),w.tags.get('wikidata'))

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
    temp_node_ref_list =[]
    for key in node_class_dict.keys():
        for node in node_class_dict[key]:
            if node.ref == None:
                node_class_dict[key].remove(node)
        node_class_dict[key] = sorted(node_class_dict[key], key = operator.attrgetter('ref'))

    return node_class_dict






if __name__ == "__main__":
    #print(returndistance_dict())
    print(get_ref_from_name('本所吾妻橋'))
    print(returndistance_dict())
    #print(return_node_dict())
    #print(count_way_distance('E04','E05'))
