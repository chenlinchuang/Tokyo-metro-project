import osmium as o
import lxml.etree as etree

#Parse osm
tree = etree.parse('export_new.osm')
root = tree.getroot()
string_test = '<tag k="ref" v="G01"/><tag k="source" v="Knowledge"/><tag k="ref" v="F16"/><tag k="wikipedia" v="ja:渋谷駅"/><tag k="ref" v="DT01;Z01"/>'

def ref_update(name,ref):
    ref_list = ref.split(';')
    for node_elem in root.findall('.//node'):
        if node_elem.find('tag') != None:
            if node_elem.find('tag').attrib['k'] == 'ref':
                print(node_elem.find('tag').attrib['v'])
            
        for node in node_elem.findall('.//tag[@v = "'+ name +'"]'):
            if ref != '':
                ref_element = etree.Element('tag', {'k':'ref','v':ref})
                node.append(ref_element)
    #tree.write('export_new.osm',encoding="utf-8",pretty_print=True)

ref_update('日比谷','I07;M06')
