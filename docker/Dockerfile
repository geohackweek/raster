FROM continuumio/anaconda
RUN apt-get install -y gcc g++ tar git curl nano wget dialog net-tools build-essential pyqt4-dev-tools
RUN conda install rasterio numpy cython shapely jupyter
RUN pip install gdal
RUN pip install pygeoprocessing
RUN mkdir /data /notebooks
COPY /data/ /data
# annoyingly, the conda install doesn't set this environment variable.
ENV GDAL_DATA /opt/conda/share/gdal
RUN pip install greenwich
