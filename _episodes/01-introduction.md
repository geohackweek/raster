---
title: "Introduction: Working with Raster Data"
teaching: 5
exercises: 0

---

## Prerequisites:

* GDAL binaries and GDAL python bindings installed on your system
* Python 2 with packages:
    * ``numpy``
    * ``rasterio``
    * ``pygeotools``
    * ``pygeoprocessing>0.4``


## Alternate setup via docker

A docker image with jupyter notebooks and a prebuilt conda environment is
available at
[geohackweek2016/rastertutorial](https://hub.docker.com/r/geohackweek2016/rastertutorial/).
Running these commands will pull the latest version of the raster tutorial
image (about 5GB download), and run the jupyter notebook server.

~~~
$ docker pull geohackweek2016/rastertutorial
$ docker run -ti -p8888:8888 geohackweek2016/rastertutorial
~~~
{: .shell}

Something like this will be printed to standard out, so just open this URL in
your browser to use the jupyter notebooks. 

    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://localhost:8888/?token=<some token>

