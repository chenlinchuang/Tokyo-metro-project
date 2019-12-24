import osmium as o
import lxml.etree as etree

#Parse osm
tree = etree.parse('export_new.osm')
root = tree.getroot()
string_test = '<tag k="ref" v="G01"/><tag k="source" v="Knowledge"/><tag k="ref" v="F16"/><tag k="wikipedia" v="ja:渋谷駅"/><tag k="ref" v="DT01;Z01"/>'

print(string_test.split('ref'))
ref_list =[]
for i in range(1,len(string_test.split('ref'))):
    ref_list.append(string_test.split('ref')[i].split('"')[2])

print((';').join(ref_list))
