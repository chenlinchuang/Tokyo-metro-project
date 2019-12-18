import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPoint
from shapely.geometry import Point
gdf = gpd.read_file('export.geojson')
way_index_list = []
node_index_list = []
for rows in range(gdf.shape[0]):
    if gdf.loc[rows,'id'].startswith('way/'):
        way_index_list.append(rows)

for rows in range(gdf.shape[0]):
    if gdf.loc[rows,'id'].startswith('node/'):
        node_index_list.append(rows)
nodes_gdf = gdf.iloc[node_index_list,:]
ways_gdf = gdf.iloc[way_index_list,:]
delete_ways_column_list = []
delete_nodes_column_list = []

for columns in range(gdf.shape[1]):
    if ways_gdf.iloc[0,columns] != None:
        delete_ways_column_list.append(columns)

for columns in range(gdf.shape[1]):
    if ways_gdf.iloc[0,columns] != None:
        delete_nodes_column_list.append(columns)

rel_index_list =[]
for rows in range(ways_gdf.shape[0]):
    if str(gdf.loc[rows,'@relations']).startswith('[ { "role": "", "rel": 443284'):
        rel_index_list.append(rows)



ways_gdf = ways_gdf.iloc[rel_index_list,delete_ways_column_list]
nodes_gdf = nodes_gdf.iloc[:,delete_nodes_column_list]

def lengths(line):
    return line.length
def linestring_to_points(feature,line):
    if str(type(line)) == "<class 'shapely.geometry.linestring.LineString'>":
        return {feature:line.coords}
    else:
        return {feature:line.exterior.coords}

def poly_to_points(feature,poly):
    return {feature:poly.exterior.coords}

ways_gdf['length'] = ways_gdf.apply(lambda l : lengths(l['geometry']), axis = 1)
ways_gdf['points'] = ways_gdf.apply(lambda l: linestring_to_points(l[0],l['geometry']),axis=1)
print(ways_gdf.iloc[1,-1])
print(tuple(ways_gdf.iloc[1,-1]['way/664646723'][0]))
for rows in range(nodes_gdf.shape[0]):
    list_nodes = str(nodes_gdf.iloc[rows,-1]).lstrip('POINT ').split(' ')
    tuple_nodes = (float(list_nodes[0][1:]),float(list_nodes[1][:-1]))
    if tuple_nodes == tuple(ways_gdf.iloc[1,-1]['way/664646723'][0]):
        print(tuple_nodes)

#for rows in range(ways_gdf.shape[0]):
#    print(Point(ways_gdf.loc[rows, 'geometry']))
#gdf.geometry = gdf.geometry.apply(lambda x: Point(list(x.exterior.coords)))
#print(ways_gdf.head())



'''
gdf = gpd.read_file('export.geojson')
count = 0
nodes_index_list = []
lines_reference_list = ['A','I','S','E','G','M','H','T','C','Y','Z','N','F']
#print(gdf.head())
class Relations:
    
    def __init__(self,id):
        self.id = id
        self.ref = ref
        self.previous_node = self
    def get_previous_node(self):
        self.ref[1:]
    pass

for i in range(len(lines_reference_list)):
    a = Relations(lines)

for rows in range(gdf.shape[0]):
    if gdf.loc[rows,'id'].startswith('node/') and 'H' in str(gdf.loc[rows,'ref']):
        nodes_index_list.append(rows)

for rows in range(gdf.shape[0]):
    if gdf.loc[rows,'id'].startswith('node/') and gdf.loc[rows,'ref'].startswith('G'):
        nodes_index_list.append(rows)

nodes_gdf = gdf.loc[nodes_index_list,:]
print(nodes_gdf.loc[:,'ref'])
#print(nodes_gdf)
'''