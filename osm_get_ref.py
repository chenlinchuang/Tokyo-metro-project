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
# Add driver
driverPath = 'geckodriver.exe'
# Set preference for geojson download
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.dir', 'g:\\')
profile.set_preference('browser.download.folderList', 0)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')
# Set browser
browser = webdriver.Firefox(executable_path = driverPath, firefox_profile=profile)

url_overpass = 'https://overpass-turbo.eu/'
browser.get(url_overpass)

# Css selector process to avoid textarea hidden caused by xpath
# Textarea is an attribute whose main function belongs to class div, name "CodeMirror"

browser.find_element_by_xpath("/html/body/div[@id='navs']/div[@class='nav']/div[@class='tabs']/a[@class='t button Data']").click()
time.sleep(2)
search_elem = browser.find_elements_by_css_selector("div.CodeMirror textarea")


all_node_list = []

class Node:
    def __init__(self, id, name, location, ref, isTransferStation, stop):
        self.id = id
        self.name = name
        self.location = location
        self.ref = ref
        self.isTransferStation = isTransferStation
        self.stop = stop


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


def get_ref(name):
    search_elem[0].send_keys(Keys.CONTROL + "a")
    search_elem[0].send_keys(Keys.DELETE)
    # XQuery language
    # Overpass QL
    search_elem[0].send_keys('[out:xml][timeout:25];' +           # output format:xml                               
    '(' + 'node["name"="'+
     name +
     '"]["railway" = "station"]["station" = "subway"]\n' +
    '(35.4,139.5,36.0,140.0);\n' +
    '); \
    out; \
    >; \
    out skel qt; \
    ')

    # Run overpass API
    search_elem[0].send_keys(Keys.CONTROL,Keys.ENTER)
    time.sleep(5)
    search_elem[1].send_keys(Keys.CONTROL + "a")
    new = search_elem[1].get_attribute('value').split('ref')
    ref_list =[]
    for i in range(1,len(new)):
        ref_list.append(new[i].split('"')[2])
    if len(ref_list) > 1:
        if 'html' in ref_list[-1]:
            ref_list = ref_list[:-1]
    return (';').join(ref_list)



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


def ref_update(name,ref):
    ref_list = ref.split(';')
    for node_elem in root.findall('.//node'):
        for node in node_elem.findall('.//tag[@v = "'+ name +'"]'):
            if node.findall('.//tag[@k = "ref"]'):
                break
            else:
                if ref != '':
                    ref_element = etree.Element('tag', {'k':'ref','v':ref})
                    node.append(ref_element)
    tree.write('export_new.osm',encoding="utf-8",pretty_print=True)

get_ref_node_list =[]
# find station without reference
for node in all_node_list:
    if node.ref == None and node.stop == 'stop_position':
        get_ref_node_list.append(node.name)

get_ref_node_list = list(set(get_ref_node_list))
print(get_ref_node_list)

print(get_ref('明治神宮前〈原宿〉'))
#for name in get_ref_node_list:
    #ref_update(name,get_ref(name))



