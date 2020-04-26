FROM continuumio/miniconda3
COPY /app /app
WORKDIR /app
RUN conda install -c conda-forge geojson scikit-learn && conda install -c pyviz geoviews geopandas paramnb parambokeh 
EXPOSE 7000
CMD ["bokeh", "serve", "--port", "7000","--prefix", "/taxi", "--allow-websocket-origin=*", "claster.py", "forecast.py"]
