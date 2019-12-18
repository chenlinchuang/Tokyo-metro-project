import osmium as o
import sys
from haversine import haversine, Unit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import lxml.etree as etree
from io import StringIO, BytesIO

#Parse osm
tree = etree.parse('export.osm')
root = tree.getroot()


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
        RelationHandler.relation_way_dict[w.tags.get['ref']] = way_id_list
        RelationHandler.relation_node_dict[w.tags.get['ref']] = node_id_list


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
    def __init__(self):
        super(NodeHandler, self).__init__()
    def node(self, w):
        all_node_list.append(Node(w.id, w.tags.get('name'), w.location, w.tags.get('ref'), False, w.tags.get('railway')))


for node in all_node_list:
    temp_node_list = []
    if ';' in node.ref:
        for relation_ref in RelationHandler.relation_node_dict.keys():
            if node.id in RelationHandler.relation_node_dict[relation_ref]:
                for node_ref in node.ref.split(';'):
                    if relation_ref in node_ref:
                        node.ref = node_ref

