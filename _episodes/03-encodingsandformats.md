---
title: "Encodings, Formats and Libraries"
teaching: 5
exercises: 0

questions:
- "What sorts of formats are available for representing raster datasets?"

objectives:
- Understand the high-level data interchange formats for raster datasets.

keypoints:
- Geospatial libraries are very useful for reading, writing and transforming
  geospatial rasters
- Once a raster's pixel values have been extracted to a numpy array, they can
  be processed with more specialized libraries and routines.

---

# Libraries and File formats for raster datasets

[GDAL](http://gdal.org) (Geospatial Data Abstraction Library) is the de facto standard library for 
interact with imagery while preserving its spatial metadata.  Other libraries
exist (we'll talk about rasterio as well as GDAL in the next section of this
tutorial, and even more exist in the fields of geoprocessing (which would
include hydrological routing and other routines needed for Earth Systems
Sciences) and digital signal processing (including image classification,
pattern recognition, and feature extraction).  The primary purpose of GDAL or a
GDAL-enabled library is to read, write and transform geospatial datasets in a
way that makes sense in the context of its spatial metadata.

GDAL's support for different file formats depends on the format drivers that
have been implemented, and the libraries that are available at compile time.
To find the available formats for your current install of GDAL:

~~~
$ gdalinfo --formats
~~~
{: .shell}

    Supported Formats:
      VRT -raster- (rw+v): Virtual Raster
      GTiff -raster- (rw+vs): GeoTIFF
      NITF -raster- (rw+vs): National Imagery Transmission Format
      RPFTOC -raster- (rovs): Raster Product Format TOC format
      ...
      # There are lots more, results depend on your build

Details about a specific format can be found with the ``--format`` parameter,
or by taking a look at the
[formats list on their website](http://www.gdal.org/formats_list.html).

~~~
$ gdalinfo --format GTiff
~~~
{: .shell}

> ## A note about libraries
> Because of its broad support for raster formats, few geospatial
> libraries exist that do not depend on GDAL.  Even the popular python library
> ``rasterio`` has a low-level dependency on the GDAL project, though this
> dependency is managed in a way that in some ways improves the utility of
> GDAL.
{: .callout}


# Programming Model

Because rasters are images, they are best thought of as 2-dimensional arrays.  If we
have multiple bands, we could think of an image as a 3-dimensional array.
Either way, we are working with arrays (matrices) of pixel values, which in the
python programming language are best represented by numpy arrays.

For this tutorial, we'll perform basic operations with numpy arrays extracted
from geospatial rasters.  For more information about multidimensional array
analysis, take a look at Thursday's tutorial on 
[N-Dimensional Arrays](https://geohackweek.github.io/nDarrays).



