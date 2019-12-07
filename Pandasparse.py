import geopandas as gpd
import matplotlib.pyplot as plt
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
'''
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