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

## 1. Background

GDAL is a powerful library for reading, writing and warping raster datasets,
and is nearly ubiquitous because of the number of file formats that it supports
and languages for which it has bindings.  There are a variety of geospatial
libraries available on the python package index, and almost all of them depend
on GDAL.  One such python library developed and supported by Mapbox,
``rasterio``, builds on top of GDAL's many features, but provides a more
pythonic interface and supports many of the features and formats that GDAL
supports.

**When should you use GDAL?**
* For reading, writing and warping raster datasets.
* If you need to read or write a raster that's in an uncommon format.
* You have sufficient access on your computer to install a low-level library.

**When should you use ``rasterio`` instead of GDAL?**
* You want to be able to ``pip install`` a functional geospatial library.
* If GDAL's functional quirks are throwing a wrench in your geoprocessing.
* ``rasterio`` provides some convenient plotting routines based on ``matplotlib``.
* Provides the same functionality as GDAL in many cases, but with more familiar, pythonic interface.

**When might these not be the best tools?**
* GDAL and rasterio don't provide geoprocessing routines, but are usually just part of a geospatial workflow.
* Other tools use GDAL and/or rasterio to provide domain-specific spatial processing routines.
* For polished map creation and interactive visualization, a desktop GIS software may be a better, more fully-featured choice.

## 2. Set up packages and data files

We'll use these throughout the rest of this tutorial.

{% highlight python %}
%matplotlib inline

from osgeo import gdal
import rasterio
from matplotlib import pyplot

# here's an ASTER DEM we'll use for our demo
DEM = 'datasets/N37W120.tif'
{% endhighlight %}


## 3. Inspecting a Raster

When it comes down to it, a geospatial raster is just an image with some
geospatial information.  For GDAL and rasterio, reading the pixel values of a
raster is a primary function.  For both libraries, pixel values are returned as
a numpy matrix.

{% highlight python %}
ds = gdal.Open(DEM)

# Let's extract and plot the pixel values
pixel_values = ds.ReadAsArray()
pyplot.imshow(pixel_values)
pyplot.colorbar()

# and here's the geospatial projection Well-Known Text and the Affine Geotransform
print ds.GetProjection()
print ds.GetGeoTransform()
{% endhighlight %}

    PROJCS["WGS 84 / UTM zone 11N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32611"]]
    (233025.03117445827, 30.0, 0.0, 4210078.842723392, 0.0, -30.0)

Rasterio provides the same functionality, just with a slightly different interface.

{% highlight python %}
with rasterio.open(DEM) as dem_raster:
    pixel_values = dem_raster.read(1)  # band number
    print dem_raster.crs   # This is returned asa dict version of the PROJ.4 format string.
    print dem_raster.transform  # Returns the GDAL-style Affine Geotransform. (will be deprecated in rasterio 1.0)
    print dem_raster.affine     # This is the Affine transformation object providing the same information as the GT.
{% endhighlight %}

    {'init': u'epsg:32611'}
    [233025.03117445827, 30.0, 0.0, 4210078.842723392, 0.0, -30.0]
    | 30.00, 0.00, 233025.03|
    | 0.00,-30.00, 4210078.84|
    | 0.00, 0.00, 1.00|

## 4. Use Case: Calculating NDVI from Landsat 8 Imagery

The Landsat program is the longest-running satellite imagery program, with the first satellite 
in the program launched in 1972.  Landsat 8 is the latest satellite in this program, and was
launched in 2013.  Landsat observations are processed into "scenes", each of which is about 
115 miles by 115 miles, with a temporal resolution of 16 days.

The duration of the landsat program makes it an attractive source of medium-scale imagery for
temporal analyses.

The [Normalized Difference Vegetation
Index](https://en.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index) is
a simple indicator that can be used to assess whether the target, usually a
remotely-sensed raster image, contains live green vegetation.  This calculation
uses two bands of a remote dataset, the Red and Near-Infrared (NIR) bands.

TODO: render this nicely
\\[
\begin{align}
NDVI & = \frac{(NIR - Red)}{(NIR + Red)}
\end{align}
\\]

For this tutorial, we'll use the NIR and Red bands from a landsat 8 scene above
part of the central valley and the Sierra Nevada in California.  We'll be using
[Level 1 datasets](https://landsat.usgs.gov/landsat-processing-details),
orthorectified, map-projected images containing radiometrically calibrated
data. These images can be individually downloaded from a variety of sources
including:

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

### Bands

* Red: Band 4 (file: ``LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF``)
* Near-Infrared: Band 5 (file: ``LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.tif``)

Because of the longevity of the landsat mission and because different sensors
on the satellite record data at different resolutions, these bands are
individually stored as single-band raster files.  Some other rasters may store
multiple bands in the same file.

NB: Landsat scenes are distributed with a 30m pixel resolution.  For the sake
of this tutorial and the computational time on our jupyterhub instance, these
scenes have been downsampled to 120m.


{% highlight python %}
L8_RED = 'datasets/LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF'
L8_NIR = 'datasets/LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.TIF'
{% endhighlight %}

Let's start out by:

* extracting the pixel values from both of these rasters 
* calculating the NDVI
* Plotting the calculated NDVI values

As a reminder, here's the NDVI equation:

\begin{align}
NDVI & = \frac{(NIR - Red)}{(NIR + Red)}
\end{align}


{% highlight python %}
    red_ds = gdal.Open(L8_RED)
    red_band = red_ds.GetRasterBand(1)
    red_pixels = red_band.ReadAsArray()
    pyplot.imshow(red_pixels)
    pyplot.colorbar()
{% endhighlight %}
TODO: image of red band


{% highlight python %}
    nir_ds = gdal.Open(L8_NIR)
    nir_band = nir_ds.GetRasterBand(1)
    nir_pixels = nir_band.ReadAsArray()
    pyplot.imshow(nir_pixels)
    pyplot.colorbar()
{% endhighlight %}
TODO: image of nir band

Now, let's calculate the NDVI from these two matrices.

{% highlight python %}
    def ndvi(red, nir):
        """Calculate NDVI."""
        return (nir_pixels - red_pixels) / (nir_pixels + red_pixels)
    
    pyplot.imshow(ndvi(red_pixels, nir_pixels))
    pyplot.colorbar()
{% endhighlight %}
TODO: show integer division image.

The plot is filled with ``0``!  It turns out that the datatype of the returned
matrices matters a lot, and both of these rasters have pixel values that are
positive (unsigned) integers, which is also reflected in the array's numpy
dtypes.  This is probably leading to an integer division issue if we're using
python 2.

{% highlight python %}
    print gdal.GetDataTypeName(red_band.DataType), red_pixels.dtype
    print gdal.GetDataTypeName(nir_band.DataType), nir_pixels.dtype
{% endhighlight %}

    UInt16 uint16
    UInt16 uint16

Let's convert the matrices to a floating-point dtype and calculate the NDVI once again.

{% highlight python %}
    import numpy
    
    red_pixels = red_pixels.astype(numpy.float64)
    nir_pixels = nir_pixels.astype(numpy.float64)
    
    ndvi_pixels = ndvi(red_pixels, nir_pixels)
    pyplot.imshow(ndvi_pixels, cmap='RdYlGn')
    pyplot.colorbar()
{% endhighlight %}
TODO: show ndvi_invalid_nodata_areas.png

According to the [docs for Landsat 8](https://landsat.usgs.gov/collectionqualityband),
those blank areas around the edges should be ignored.  Many raster datasets
implement this with an optional **nodata value**.  If a nodata value is set,
then any pixel values that match it should be ignored.  It turns out that this
band doesn't have a defined nodata value.

{% highlight python %}
    # This band does not have a nodata value!
    print red_band.GetNoDataValue()
{% endhighlight %}

    None

It turns out that we know from the docs that there's another landsat band
(``_BQA.TIF``) for our scene that contains extra metadata about the pixels of
the scene.  In this raster, any pixels with a value of ``1`` is filler and can
be ignored.

Let's create an NDVI matrix where:
* Any pixels marked as filler in the ``_BQA.TIF`` raster are set to ``-1``.
* Any pixels where the denominator is ``0`` is also set to ``-1``.

{% highlight python %}
    L8_QA = 'datasets/LC08_L1TP_042034_20130605_20170310_01_T1_BQA_120x120.TIF'
{% endhighlight %}

{% highlight python %}
    import numpy
    
    qa_ds = gdal.Open(L8_QA)
    qa_band = qa_ds.GetRasterBand(1)
    qa_pixels = qa_band.ReadAsArray()
    
    def ndvi_with_nodata(red, nir, qa):
        ndvi = (nir - red) / (nir + red)
        ndvi[qa == 1] = -1
        return ndvi
        
    ndvi_pixels = ndvi_with_nodata(red_pixels, nir_pixels, qa_pixels)
    pyplot.imshow(ndvi_pixels, cmap='RdYlGn')
    pyplot.colorbar()
{% endhighlight %}
TODO: show ndvi_with_nodata_value.png

## 5. Save the NDVI Raster to Disk

Now, let's create an output geospatial raster and write our new NDVI values to it.

To do this, we need to tell GDAL which file format to use, if there are any
special options that should be set when the file is created, and what the
raster's dimensions should be.  We'll use the ``GTiff`` driver for this.
GeoTiff is an open format that is very well supported by GDAL and most GIS
applications.  (For a full list of supported formats, take a look at
``gdalinfo --formats``.)

{% highlight python %}
    driver = gdal.GetDriverByName('GTiff')
    new_dataset = driver.Create('ndvi.tif',
                                ds.RasterXSize,    # number of columns
                                ds.RasterYSize,    # number of rows
                                1,                 # number of bands
                                gdal.GDT_Float32)  # datatype of the raster
    new_dataset.SetProjection(ds.GetProjection())
    new_dataset.SetGeoTransform(ds.GetGeoTransform())
    
    # Now we need to set the band's nodata value to -1
    new_band = new_dataset.GetRasterBand(1)
    new_band.SetNoDataValue(-1)
    
    # And finally, let's write our NDVI array.
    new_band.WriteArray(ndvi_pixels)
{% endhighlight %}

{% highlight python %}
    # Here's the rasterio equivalent
    with rasterio.open(L8_RED) as red_raster:
        source_crs = red_raster.crs
        source_transform = red_raster.transform
    
    with rasterio.open('ndvi.tif', 'w', driver='GTIff',
                       height=ndvi_pixels.shape[0],    # numpy of rows
                       width=ndvi_pixels.shape[1],     # number of columns
                       count=1,                        # number of bands
                       dtype=rasterio.dtypes.float64,  # this must match the dtype of our array
                       crs=source_crs,
                       transform=source_transform) as ndvi_raster:
        ndvi_raster.write(ndvi_pixels, 1)  # optional second parameter is the band number to write to
        ndvi_raster.nodata = -1  # set the raster's nodata value
{% endhighlight %}

{% highlight shell %}
    !gdalinfo ndvi.tif
{% endhighlight %}

    Driver: GTiff/GeoTIFF
    Files: ndvi.tif
    Size is 1928, 1881
    Coordinate System is:
    PROJCS["WGS 84 / UTM zone 11N",
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0],
            UNIT["degree",0.0174532925199433],
            AUTHORITY["EPSG","4326"]],
        PROJECTION["Transverse_Mercator"],
        PARAMETER["latitude_of_origin",0],
        PARAMETER["central_meridian",-117],
        PARAMETER["scale_factor",0.9996],
        PARAMETER["false_easting",500000],
        PARAMETER["false_northing",0],
        UNIT["metre",1,
            AUTHORITY["EPSG","9001"]],
        AUTHORITY["EPSG","32611"]]
    Origin = (203385.000000000000000,4261815.000000000000000)
    Pixel Size = (120.000000000000000,-120.000000000000000)
    Metadata:
      AREA_OR_POINT=Area
    Image Structure Metadata:
      INTERLEAVE=BAND
    Corner Coordinates:
    Upper Left  (  203385.000, 4261815.000) (120d23'56.68"W, 38d27'19.28"N)
    Lower Left  (  203385.000, 4036095.000) (120d18'29.96"W, 36d25'27.35"N)
    Upper Right (  434745.000, 4261815.000) (117d44'54.15"W, 38d30' 8.31"N)
    Lower Right (  434745.000, 4036095.000) (117d43'42.06"W, 36d28' 4.47"N)
    Center      (  319065.000, 4148955.000) (119d 2'45.84"W, 37d28'11.22"N)
    Band 1 Block=1928x1 Type=Float64, ColorInterp=Gray
      NoData Value=-1



[landsat8preview]: https://landsat-pds.s3.amazonaws.com/L8/042/034/LC80420342013156LGN00/LC80420342013156LGN00_thumb_small.jpg "Landsat 8 preview image over the California Central Valley"
