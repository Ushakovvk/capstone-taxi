# Загрузка модулей
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt 
import pickle
import geojson
import geopandas
from sklearn.cluster import KMeans
import holoviews as hv, geoviews as gv, param, paramnb, parambokeh
from geoviews.tile_sources import EsriImagery
hv.extension('bokeh', logo=False)

#Загрузка данных

with open('data/mesh.pkl', 'rb') as f:
    mesh = pickle.load(f)
with open('data/features_data.pkl', 'rb') as f:
    features = pickle.load(f)
    
# Класс интерактивной карты

class NYCTaxiExplorer(hv.streams.Stream):
    n_clusters = param.Integer(default=5, bounds=(1, 15))
    def make_view_clusters(self, **kwargs):
        model_cl = KMeans(n_clusters=self.n_clusters).fit(features)
        assignments = model_cl.labels_
        mesh['clusters'] = assignments
        polygon = gv.Polygons(mesh,vdims=['clusters']).options(width=500, height=500, alpha=0.9,
                                                  color_index='clusters', cmap='set2')
        return polygon
    
img = EsriImagery
explorer = NYCTaxiExplorer(name='Clustering of New-York Taxi')
trips = hv.DynamicMap(explorer.make_view_clusters, streams=[explorer])
plot = hv.renderer('bokeh').instance(mode='server').get_plot(img * trips)
parambokeh.Widgets(explorer,callback=explorer.event,plots=[plot.state], mode='server')