---
title: "Working with Raster Datasets"
teaching: 20
exercises: 10
questions:
  - "How can I extract pixel values from a raster dataset?"
  - "How might I write pixel values out to a new raster file?"
  - "What raster dataset formats (reading and writing) are supported?"
objectives:
  - "Understand the basic components of a raster dataset and how to access them from a python program."
  - "Perform numerical operations on pixel values."
  - "Read from and write to raster datasets."
keypoints:
  - GDAL is a 'swiss army knife' for raster operations, but is pretty low-level.
  - "Rasterio provides much of GDAL's functionality and is easier to install, but supports fewer formats out of the box."
  - "Pixel values of rasters can be extracted to a numpy array"
---

* Demonstrate how to open and plot a geotiff
* Demonstrate how to create a new geotiff
* Let's talk about numpy arrays briefly (n-dimensional arrays will be covered on Thursday)
* Read a raster in and explore it a bit as a numpy array.
    * talk about how masking can apply here.  Rasterio vs. GDAL differences.
* Talk about available libraries and various support for formats (rasterio vs. GDAL, for example)
    * There are other libraries for reading rasters, but almost all wrap GDAL because of its utility.
* Use GDALinfo to demonstrate

# Landsat Imagery

The Landsat program is the longest-running satellite imagery program, with the first satellite 
in the program launched in 1972.  Landsat 8 is the latest satellite in this program, and was
launched in 2013.  Landsat observations are processed into "scenes", each of which is about 
115 miles by 115 miles, with a temporal resolution of 16 days.

The duration of the landsat program makes it an attractive source of medium-scale imagery for
temporal analyses.

For this tutorial, we'll use the NIR and Red bands from a landsat 8 scene above 
part of the central valley and the Sierra Nevada in California.  We'll be using 
[Level 1 datasets](https://landsat.usgs.gov/landsat-processing-details), 
orthorectified, map-projected images containing radiometrically calibrated data. 
These images can be individually downloaded from a variety of sources including:

* [USGS EarthExplorer](https://earthexplorer.usgs.gov/) (Account required for download)
* [Amazon AWS](https://aws.amazon.com/public-datasets/landsat/)

The specific scene we'll be using is:

* Collection: `LC08_L1TP_042034_20130605_20170310_01_T1` (Available from USGS Earth Explorer)
* Pre-collection: `LC80420342013156LGN00` ([Available from Amazon AWS](https://landsat-pds.s3.amazonaws.com/L8/042/034/LC80420342013156LGN00/index.html))

More information on Landsat collections here: [https://landsat.usgs.gov/landsat-collections](https://landsat.usgs.gov/landsat-collections)

|--------------------------------------------------|
| Landsat 8 preview over the CA Central Valley     |
|--------------------------------------------------|
|![Preview of our landsat 8 scene][landsat8preview]|
|--------------------------------------------------|

# Set up package imports and data files

We'll use these throughout the rest of the tutuorial.

{% highlight python %}
%matplotlib inline
from matplotlib import pyplot

# These two libraries are both very useful for reading and writing raster
# datasets.  Rasterio includes some plotting functionality, which we'll use 
# here as well.
from osgeo import gdal
import rasterio

# We can use these constants for the paths so you don't have to type them out!
# If you've cloned this repository, these files will already be here.

L8_RED = 'datasets/LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF'
L8_NIR = 'datasets/LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.TIF'
{% endhighlight %}


# Reading pixel values

{% highlight python %}
# We can see that GDAL has opened the dataset properly by checking the value of ``dataset``.
dataset = gdal.Open(L8_RED)
print dataset  # <osgeo.gdal.Dataset; proxy of <Swig Object of type 'GDALDatasetShadow *' at 0x1023394e0> >
band_matrix = dataset.ReadAsArray()
print band_matrix
{% endhighlight %}

{% highlight python %}
with rasterio.open(L8_RED) as red:
    band_matrix = red.read(1)
    print band_matrix
{% endhighlight %}
