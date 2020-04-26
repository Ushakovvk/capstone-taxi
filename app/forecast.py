import pandas as pd
import numpy as np
import pickle
import geojson
import geopandas
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt 
import holoviews as hv, geoviews as gv, param, paramnb, parambokeh
from geoviews.tile_sources import EsriImagery
from holoviews.streams import Selection1D
hv.extension('bokeh',logo=False)
predict_data = pd.read_csv('data/predict_data.csv',index_col='datetime',parse_dates=['datetime'])
trips_data = pd.read_csv('data/trips_data.csv',index_col='datetime',parse_dates=['datetime'])
with open('data/list_region.pkl','rb') as f:
    list_region = pickle.load(f)
regions = pd.read_csv('data/regions.csv',sep=';',index_col='region')
regions = regions.loc[list_region,:]
feature = []
# Ячейки только с ненулевыми значениями
for n in regions.itertuples():
    coord = []
    # Образуем замкнутый полигон с id = номер ячейки
    coord.append((n[1],n[4]))
    coord.append((n[2],n[4]))
    coord.append((n[2],n[3]))
    coord.append((n[1],n[3]))
    coord.append((n[1],n[4]))
    feature.append(geojson.Feature(geometry=geojson.Polygon([coord]),id=n[0]))
feature_collection = geojson.FeatureCollection(feature)
df = geopandas.GeoDataFrame.from_features(feature_collection)
df['region'] = list_region
list_date = [x.strftime('%Y-%m-%d') for x in pd.date_range(start='2016-06-02',end='2016-07',freq='D',closed='left').date]
print('ok')
class NYCTaxiExplorer(hv.streams.Stream):
    hour = param.Integer(default=12,bounds=(0, 23))
    date = param.ObjectSelector(default=list_date[0], objects=list_date)

    def make_view_trips(self, **kwargs):
        df['pickup'] = trips_data.loc[f'{self.date}-{self.hour:02d}',:].values

        pickup = gv.Polygons(df,vdims=['region','pickup']).options(width=500, height=500,tools=['hover'],alpha=0.5,
                                                  color_index='pickup', colorbar=True, toolbar='above',hover_color='red')
        return pickup
    
    def make_view_predict(self, **kwargs):
        df['predict'] = predict_data.loc[f'{self.date}-{self.hour:02d}',:].values
        predict = gv.Polygons(df,vdims=['region','predict']).options(width=500, height=500,tools=['hover'],alpha=0.5,
                                                  color_index='predict', colorbar=True, toolbar='above',hover_color='red')
        return predict
    
    def regression(self, index):
        if not index:
            index = [0]
        series = pd.DataFrame(columns=['time','pickup'])
        series['pickup'] = trips_data.loc['2016-06',str(list_region[index[0]])].values
        series['time'] = trips_data.loc['2016-06',str(list_region[index[0]])].index
        predict = pd.DataFrame(columns=['time','predict'])
        predict['predict'] = predict_data.loc['2016-06',str(list_region[index[0]])].values
        predict['time'] = predict_data.loc['2016-06',str(list_region[index[0]])].index
        reg = (hv.Curve(series,label='История').options(width=1000, height=400,framewise=True) * hv.Curve(predict,label='Прогноз').options(width=1000, height=400,framewise=True)).relabel(f'Ячейка №{list_region[index[0]]}')
        return reg
    
    def make_curve(self):
        reg = hv.DynamicMap(self.regression, kdims=[], streams=[stream])
        return reg
explorer = NYCTaxiExplorer(name='Forecast of New-York Taxi')
trips = hv.DynamicMap(explorer.make_view_trips, streams=[explorer])
predict = hv.DynamicMap(explorer.make_view_predict, streams=[explorer])
img = EsriImagery
polygons = gv.Polygons(df,vdims=['region']).options(width=500, height=500,tools=['tap'],alpha=0)
stream = Selection1D(source=polygons)
curve = hv.DynamicMap(explorer.regression, kdims=[], streams=[stream])
dmap = ((trips * img * polygons).relabel('История') + (predict * img * polygons).relabel('Прогноз') + curve).cols(2)
plot = hv.renderer('bokeh').instance(mode='server').get_plot(dmap)
parambokeh.Widgets(explorer, view_position='right', callback=explorer.event, plots=[plot.state], mode='server')
