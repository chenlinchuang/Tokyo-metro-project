import geopandas as gpd
import requests
import geopandas as gpd
from shapely.geometry import shape

r = requests.get("export.json")
r.raise_for_status()

data = r.json()
for d in data:
    d['the_geom'] = shape(d['the_geom'])

gdf = gpd.GeoDataFrame(data).set_geometry('the_geom')
gdf.head()