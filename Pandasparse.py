import geopandas as gpd
import matplotlib.pyplot as plt
gdf = gpd.read_file('export.geojson')
count = 0
nodes_index_list =[]
'''
for rows in range(gdf.shape[0]):
    if gdf.loc[rows,'id'].startswith('node/') and str(gdf.loc[rows,'ref']).startswith('H'):
        nodes_index_list.append(rows)
'''
for rows in range(gdf.shape[0]):
    if gdf.loc[rows,'id'].startswith('node/') and gdf.loc[rows,'colour'] == 'gray':
        nodes_index_list.append(rows)


nodes_gdf = gdf.loc[nodes_index_list,:]
print(nodes_gdf.loc[:,'name'])
#print(nodes_gdf)
