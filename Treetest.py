import xml.etree.ElementTree as ET
import lxml.etree as etree
from io import StringIO, BytesIO
utf8_parser = etree.XMLParser(encoding='utf-8')
tree = etree.parse('export.osm')
root = tree.getroot()

def ref_update(name,ref):
    for elem in root.findall('.//node'):
        if elem.findall('.//tag[@v = "'+ name +'"]'):
            print(elem.attrib['id'])
            ref_element = etree.Element('tag', {'k':'ref','v':ref})
            elem.append(ref_element)
    tree.write('export.osm',encoding="utf-8",pretty_print=True)