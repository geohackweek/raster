---
title: "Using GDAL"
teaching: 20
exercises: 10
questions:
- "What functionality does GDAL offer?"
- "What raster dataset formats are supported?"
- "How do I interact with raster data within a python program?"
objectives:
- "Understand the basic components of a raster dataset and how to access them
with GDAL"
- "Read from and write to raster datasets"
- "Perform numpy operations on a raster's values"
keypoints:
- "GDAL is extremely useful for reading/writing/transforming raster datasets"
- "GDAL usually ships with useful command-line utilities"
- "Errors can be handled pythonically"
- "Pixel values can be extracted to a numpy array"
- "Raster attributes can usually be read without reading pixel values"
---

# What is GDAL (Geospatial Data Abstraction Library)?

* C/C++ library for reading, writing, and reprojecting raster and vector datasets
    * Provides a single abstract data model for interacting with all supported formats
    * Spatial reprojections provided by [PROJ.4](http://proj4.org/), a library for 
      performing conversions between cartographic projections (currently maintained
      by Frank Warmerdam).
* Originally developed as a side project by Frank Warmerdam (first release in 2000)
* Major open-source member of the Open Source Geospatial Foundation
* OGR (GDAL-provided library for handing vector data) is also part of the project
* Together, GDAL/OGR contains 1.1M lines of code (not including comments and whitespace
* Almost ubiquitous in geospatial applications

# Supported Formats:

As of the latest version of GDAL, 142 formats are supported, but builds for various platforms may omit support for some formats.  The docker images for this tutorial include a GDAL build with support for 124 formats, including a few that have both raster and vector layers.

>## Not all formats are supported equally
>GDAL's drivers do not support all formats equally, and differences are 
> listed in `gdalinfo --formats`.
> * ``ro`` - read-only support
> * ``rw`` - reading and writing to existing files (and making copies) supported
> * ``rw+`` - reading, writing and creation of new files supported
> * ``v`` - the format supports streaming through virtual filesystem API.  Streaming sources include compressed archives (such as ``.tar.gz``) and remote file servers (such as HTTP, FTP)
> * ``s`` - the format support subdatasets
{: .callout}

{% highlight bash%}
$ gdalinfo --formats
Supported Formats:
  VRT -raster- (rw+v): Virtual Raster
  GTiff -raster- (rw+vs): GeoTIFF
  NITF -raster- (rw+vs): National Imagery Transmission Format
  RPFTOC -raster- (rovs): Raster Product Format TOC format
  ...
  # There are lots more, results depend on your build
{% endhighlight %}

Specifics about each format can be found with the ``--format`` parameter.  Let's take a look
at the GeoTiff format, which is well-supported and has many possible creation options.

{% highlight bash%}
$ gdalinfo --format GTiff
{% endhighlight %}

GDAL also has prose documentation available for each format, including detailed information
about creation options available on their website at: 
[http://www.gdal.org/formats_list.html](http://www.gdal.org/formats_list.html).

## GDAL CLI Utilities

GDAL provides a number of command-line utilities to automate common processes.  To see the utilities available on your system:

{% highlight text%}
$ ls -la /usr/local/bin/gdal*
{% endhighlight %}

A full listing of GDAL utilities is available on the [GDAL website](http://gdal.org/gdal_utilities.html). A few that might be particularly useful to you include:

* ``gdalinfo`` - Describe relevant information about a raster, will include the Raster Attribute Table in XML, if one exsits.
* ``gdal_translate`` - Copy contents of an existing raster image to a new one, with new creation options.
* ``gdal_merge.py`` - We'll use this to merge our two DEMs together into a single raster file.
* ``gdalmanage`` - Identify raster datatypes, and/or delete, rename, and copy files in a dataset. 

Each of these GDAL utilities automate certain pieces of commonly-used functionality.  Python scripts can also be used as examples for how to use the GDAL python API for those
writing software that interfaces directly with the SWIG API.

## Access to GDAL libraries

GDAL is a C++ library, but you don't need to write your software in C++ to use it.
Official bindings are available for other languages: 
Python [PyPI](http://pypi.python.org/pypi/GDAL), C#, Ruby, Java, Perl, and PHP.

Of course, you can write your software in C++ if you like :)  For the purposes
of this tutorial, we'll interact with the official python bindings.

> ## A note about pythonic behavior
>
> There are several ways that GDAL's bindings behave that may catch you by surprise.
> This tutorial will avoid most of them, but it's good to know that these exist if you
> end up writing software that uses GDAL.  For the full list of gotchas, take a look at
> [https://trac.osgeo.org/gdal/wiki/PythonGotchas](https://trac.osgeo.org/gdal/wiki/PythonGotchas)
{: .callout}

# Sample datasets

We'll use a couple of datasets for this tutorial, all of which are in ``/data``
on the ``geohackweek2016/raster`` docker image.

These datasets are projected in WGS84/UTM zone 11N, as they are located in the southern
Sierra Nevada mountains in California.

## ASTER DEMs

ASTER (Advanced Spaceborne Thermal Emission and Reflection Radiometer) is a remote
sensor operated as a collaboration between NASA and Japan's Ministry of Economy,
Trade and Industry (METI).  Located on board the
[Terra](https://en.wikipedia.org/wiki/Terra_(satellite)) satellite that was launched
in 1999, raw ASTER data provides imagery across 14 bands at resolutions between 15
and 90 meters.  The sample datasets we'll be using today are from the ASTER Global
DEM (GDEM) version 2, and have been projected into the WGS84/UTM11N coordinate system.

|-----------------------|-----------------------|
| ``/data/N38W120.tif`` | ``/data/N37W120.tif`` |
|-----------------------|-----------------------|
| ![DEM 1](N38W120.png) | ![DEM 1](N37W120.png) |
|-----------------------|-----------------------|
| ASTER GDEM is a product of METI and NASA.     |
|-----------------------------------------------|

Let's take a look at one of these rasters with ``gdalinfo``:

~~~
$ gdalinfo /data/N38W120.tif
~~~
{: .shell}

Note a few relevant details about the raster:

	* Only 1 band in this raster
    * Data type of raster is 16-bit integer
    * The raster is compressed with ``DEFLATE`` mode
    * Pixel values range from 1272 - 3762
    * Note block size is a whole row of pixels.

## Land-Use / Land-Cover

This Land-use/land-cover raster is a subset of a global climatology analysis
based on Moderate-resolution imaging spectroradiometer (MODIS) datasets at a 
1km scale.  The MODIS sensor is on board the same satellite as the ASTER 
sensor, and records data at a scale between 250m and 1km across 36 bands.
This raster dataset has been clipped to a region that includes the southern
portion of the Sierra Nevada mountain range.

|------------------------------------------------------------------|
| ``/data/landcover.tif``              							   |
|------------------------------------------------------------------|
| ![LULC](landcover.png)             							   |
|------------------------------------------------------------------|
| Source: [USGS](http://landcover.usgs.gov/global_climatology.php) |
|------------------------------------------------------------------|

# Using GDAL

We'll interact primarily with GDAL through their official python bindings.

## Begin by importing these libraries

~~~
from osgeo import gdal
~~~

### Open the dataset

First we open the raster so we can explore its attributes, as in the introduction.  GDAL will detect the format if it can, and return a *gdal.Dataset* object.

~~~
ds = gdal.Open('/data/N37W120.tif')
~~~
{: .python}

You'll notice this seemed to go very fast. That is because this step does not 
actually ask Python to read the data into memory. Rather, GDAL is just scanning 
the contents of the file to allow us access to certain critical characteristics.

>## Filepath encodings:
> GDAL expects the path to the raster to be ASCII or UTF-8, which is a common 
> filesystem encoding on linux and macs. Windows is often
> [ISO-8859-1 (Latin-1)](https://en.wikipedia.org/wiki/ISO/IEC_8859-1), or else
> uses a codepage most similar to your locale.
> This will only be an issue with python 2.x, as the ``str`` type in python3 is
> assumed to be encoded as UTF-8.
{: .callout}

>## Note on Error Handling:
> While GDAL's python bindings have become much more pythonic, errors are not
> automatically raised as python exceptions.  Instead, the default error behavior
> is to print a message to your stdout console and return ``None`` from the operation.
>
> If you experience ``AttributeError: 'NoneType' object has no attribute 'foo'``, this
> may be why.
>
> #### Pythonic Error Handling
> ~~~
> gdal.UseExceptions()
> ~~~
> {: .python}
{: .callout}



### Inspecting the Dataset:

Since rasters can be very, very large, GDAL will not read its contents into 
memory until we need to access those values.  Various formats support different
amounts of data (GeoTiff, should support exabytes-large files), so GDAL provides
various methods to access attributes of the dataset without reading in all
of the pixel values.

As with any python library, the methods available from the ``ds`` object can be
read through with ``help()``.

~~~
help(ds)
~~~
{: .python}

### Driver

Since GDAL will happily open any dataset it knows how to open, one of the attributes
we can query is the driver that was used:

~~~
ds.GetDriver().LongName
ds.GetDriver().ShortName
~~~
{: .python}

You'll recognize these names from when we previously looked into ``gdalinfo --format(s)``.  Either of these format names are acceptable for internal GDAL or if we're creating our own raster datasets.

### Coordinate Reference System:

Each dataset can have a coordinate reference system defined, which we can retrieve as Well-Known Text (WKT).

~~~
ds.GetProjection()
~~~
{: .python}

This isn't especially easy to read, but it is a valid projection string.  We can also print this
nicely with a couple of extra steps, using the ``osgeo.osr`` module for manipulating spatial references.

~~~
from osgeo import osr

raster_wkt = ds.GetProjection()
spatial_ref = osr.SpatialReference()
spatial_ref.ImportFromWkt(raster_wkt)
print spatial_ref.ExportToPrettyWkt()
~~~
{: .python}

If you're familiar with GIS software, the PROJ.4 projection string may be more useful:

~~~
print spatial_ref.ExportToProj4()
~~~
{: .python}

### Dimensions

Dimensions are accessed as attributes of the Dataset class.  X size represents the 
number of columns, Y size represents the number of rows.

~~~
ds.RasterXSize
ds.RasterYSize
~~~
{: .python}


### Block Sizes

Rasters are stored on disk in contiguous chunks called _blocks_, which become very useful
when trying to optimize your application for speed of execution.  We'll cover more on that
later, but for now, you can access the block size like so:

~~~
ds.GetBlockSize()
~~~
{: .python}

In this case, the blocksize is one row at a time, but different rasters can be laid
out differently on disk (represented by different block sizes).  The landcover
raster, for example, has a very different blocksize:

~~~
lulc_ds = gdal.Open('/data/landcover.tif')
lulc_ds.GetBlockSize()
~~~
{: .python}

![LULC blocksizes](landcover-blocks.png)

## Reading Raster Values

Several GDAL objects have ``ReadAsArray()`` methods:

* ``gdal.Dataset``
* ``gdal.Band``
* ``gdal.RasterAttributeTable``

~~~
array = ds.ReadAsArray()
~~~
{: .python}

In our case, the raster ``/data/N37W120.tif`` only contains a single band, so 
both ``ds.ReadAsArray()`` and ``band.ReadAsArray()`` will return the same data.
The number of bands can be checked before loading the array:

~~~
ds.RasterCount
~~~
{: .python}

Even if there is only 1 band in the raster, you can still retrieve the band object
before accessing the raster's array. Note that some attributes, especially 
nodata value and band-specific metadata.
For a full listing of band attributes, see the 
[GDAL Data Model documentation](http://www.gdal.org/gdal_datamodel.html) and the 
[python API docs](http://www.gdal.org/python/osgeo.gdal.Band-class.html).

~~~
band = ds.GetRasterBand(1)
array = band.ReadAsArray()
nodata = band.GetNoDataValue()
metadata = band.GetMetadata()
~~~
{: .python}


While ``ReadAsArray()`` can be used to read the whole array into memory,
you can also specify a subset of the raster or band to open with a few
optional parameters to ``ReadAsArray()``.

~~~
band = ds.GetRasterBand(1)
full_array = band.ReadAsArray()

# Start at index (100, 100) and read in an array 250 pixels wide
array_part = band.ReadAsArray(
    xoff=100,
    yoff=100,
    xsize=250,
    ysize=250)
~~~
{: .python}

Note that while the size of ``array_part`` is exactly what we requested, GDAL has to
read in an enormous number of pixels in order to obtain the small, requested subset.

![Blocks read in and discarded for a small window of values](N37W120-read-blocks.png)

## Copying Raster Datasets

### Copying files without GDAL:

~~~
import os
os.copyfile(
    '/path/to/raster.tif',
    '/path/to/newraster.tif')
~~~
{: .python}


### Copying files with GDAL CLI utilities

~~~
gdalmanage copy /data/N37W120.tif /tmp/N37W120_copy.tif
~~~
{: .shell}


### Copying files with GDAL SWIG bindings 
~~~
from osgeo import gdal
driver = gdal.GetDriverByName('GTiff')
new_ds = driver.CreateCopy('/path/to/new_raster.tif', ds)
new_ds = None  # flush the dataset to disk and close the underlying objects.
~~~
{: .python}


### Creating new files with GDAL

~~~
from osgeo import gdal
driver = gdal.GetDriverByName('GTiff')
new_ds = driver.Create(
    'path/to/new_raster.tif',
    400,  # xsize
    600,  # ysize
    1,    # number of bands
    gdal.GDT_Float32,  # The datatype of the pixel values
    options=[  # Format-specific creation options.
        'TILED=YES',
        'BIGTIFF=IF_SAFER',
        'BLOCKXSIZE=256',  # must be a power of 2
        'BLOCKYSIZE=256'   # also power of 2, need not match BLOCKXSIZE
    ])

# fill the new raster with nodata values
new_ds.SetNoDataValue(-1)
new_ds.fill(-1)

# When all references to new_ds are unset, the dataset is closed and flushed to disk
new_ds = None
~~~
{: .python}

## Writing to a raster

Unlike reading to an array, writing only happens at the band level.

~~~
writeable_ds = gdal.Open('/path/to/raster.tif', gdal.GA_Update)
band = writeable_ds.GetRasterBand(1)

array = band.ReadAsArray()
array += 1
band.WriteArray(array)

band = None
ds = None
~~~
{: .python}

### Other libraries that make use of GDAL:

Two libraries in particular extend GDAL to provide a more pythonic interface.

* [rasterio](https://pypi.python.org/pypi/rasterio)
    * Developed by Mapbox, this compiles against GDAL but does not require it
    in the same way that the SWIG bindings do.
    * This library focuses on providing pythonic design patterns, and tries to
    eliminate the python gotchas found in the GDAL SWIG bindings.
    * Not all raster file formats supported by GDAL are supported by rasterio.
    * Supports python versions 2 and 3.

* [greenwich](https://pypi.python.org/pypi/greenwich)
    * This is a third-party library that extends the GDAL SWIG bindings
    * Greenwich objects still allow access to the underlying GDAL objects that
    we reviewed in this section
    * Attributes of a raster are accessed in the ways that python developers
    are accustomed to.
    * Supports python 2 only.

For building geospatial web applications based on Django, be sure to check out GeoDjango:

* [GeoDjango (via postGIS)](https://docs.djangoproject.com/en/1.10/ref/contrib/gis/)


> ## How many square meters does ``/data/landcover.tif`` cover?
>
> ~~~
> lulc_ds = gdal.Open('/data/landcover.tif')
> geotransform = lulc_ds.GetGeoTransform()
> coverage_in_m = (lulc_ds.RasterXSize * math.abs(geotransform[1]) +
>   lulc_ds.RasterYSize *  math.abs(geotransform[5]))
> ~~~
> {: .python}
{: .challenge}
