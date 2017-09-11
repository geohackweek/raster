---
title: "Working with Raster Datasets"
teaching: 45
exercises: 0
questions:
  - "How can I extract pixel values from a raster dataset?"
  - "How might I write pixel values out to a new raster file?"
  - "What raster dataset formats (reading and writing) are supported?"
objectives:
  - "Understand the basic components of a raster dataset and how to access them from a python program."
  - "Perform numerical operations on pixel values."
  - "Read from and write to raster datasets."
  - "Be able to perform pixel-stack operations and write the output to a new raster."
keypoints:
  - GDAL is a 'swiss army knife' for raster operations, but is pretty low-level.
  - "Rasterio provides much of GDAL's functionality and is easier to install, but supports fewer formats out of the box."
  - "Pixel values of rasters can be extracted to a numpy array."
  - "Raster analysis in python revolves around numpy arrays as the primary data structure and programming model."
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

~~~
%matplotlib inline

from osgeo import gdal
import rasterio
import matplotlib.pyplot as plt

# here's an ASTER DEM we'll use for our demo
DEM_fn = '../data/N37W120.tif'
~~~
{: .python}


## 3. Inspecting a Raster

When it comes down to it, a geospatial raster is just an image with some
geospatial information.  For GDAL and rasterio, reading the pixel values of a
raster is a primary function.  For both libraries, pixel values are returned as
a numpy array.

~~~
ds = gdal.Open(DEM_fn)

# Let's extract and plot the pixel values
pixel_values = ds.ReadAsArray()
plt.imshow(pixel_values)
plt.colorbar()

# and here's the geospatial projection Well-Known Text and the Affine Geotransform
print ds.GetProjection()
print ds.GetGeoTransform()
~~~
{: .python}

    PROJCS["WGS 84 / UTM zone 11N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32611"]]

    (233025.03117445827, 30.0, 0.0, 4210078.842723392, 0.0, -30.0)

![Stylized, projected ASTER GDEM tile](aster_dem_demo.png)

Rasterio provides the same functionality, just with a slightly different
interface.  If you're familiary with programming in python, you've probably
seen **context managers** before.  This context manager, ``rasterio.open``
functions like the python standard library function ``open`` for opening files.
The block of code within the ``with ... as`` statement is executed once the file
is opened, and the file is closed when the context manager exits.  This
means that we don't have to manually close the raster file, as the 
context manager handles that for us.

By contrast, GDAL closes its raster dataset objects when its objects have no
active references. In our case above, we're letting all of the raster objects
go out of scope, so the cleanup happens implicitly at the end of the code.

~~~
with rasterio.open(DEM_fn) as dem_raster:
    pixel_values = dem_raster.read(1)  # band number
    print dem_raster.crs   # This is returned as a dict version of the PROJ.4 format string.
    print dem_raster.transform  # Returns the GDAL-style Affine Geotransform. (will be deprecated in rasterio 1.0)
    print dem_raster.affine     # This is the Affine transformation object providing the same information as the GT.
~~~
{: .python}

    {'init': u'epsg:32611'}
    [233025.03117445827, 30.0, 0.0, 4210078.842723392, 0.0, -30.0]
    | 30.00, 0.00, 233025.03|
    | 0.00,-30.00, 4210078.84|
    | 0.00, 0.00, 1.00|

## 4. Use Case: Calculating NDVI from Landsat 8 Imagery

The Landsat program is the longest-running satellite imagery program, with the first satellite 
launched in 1972.  Landsat 8 is the latest satellite in this program, and was
launched in 2013.  Landsat observations are processed into "scenes", each of which is approximately 
183 km x 170 km, with a temporal resolution of 16 days.

The duration of the landsat program makes it an attractive source of medium-scale imagery for
land surface change analyses.

The [Normalized Difference Vegetation
Index](https://en.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index) is
a simple indicator that can be used to assess whether the target includes healthy vegetation.  
This calculation uses two bands of a multispectral image dataset, the Red and Near-Infrared (NIR) bands.

![NDVI equation](ndvi_equation.png)

For this tutorial, we'll use the NIR and Red bands from a Landsat-8 scene above
part of the central valley and the Sierra Nevada in California.  We'll be using
[Level 1TP datasets](https://landsat.usgs.gov/landsat-processing-details),
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
L8_RED_fn = '../data/LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF'
L8_NIR_fn = '../data/LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.TIF'
{% endhighlight %}

Let's start out by:

* opening the raster datasets using the GDAL Python API
* extracting the pixel values from both of these rasters 
* calculating the NDVI
* visualizing the calculated NDVI values

As a reminder, here's the NDVI equation:

![NDVI equation](ndvi_equation.png)


~~~
red_ds = gdal.Open(L8_RED_fn)
red_band = red_ds.GetRasterBand(1)
red = red_band.ReadAsArray()
plt.imshow(red)
plt.colorbar()
~~~
{: .python}
![Matplotlib plot of the red band of the current landsat 8 scene](red_band_raw.png)


~~~
nir_ds = gdal.Open(L8_NIR_fn)
nir_band = nir_ds.GetRasterBand(1)
nir = nir_band.ReadAsArray()
plt.imshow(nir)
plt.colorbar()
~~~
{: .python}
![Matplotlib plot of the near-infrared band of the current landsat 8 scene](nir_band_raw.png)

Now, let's calculate the NDVI from these two arrays.

~~~
def ndvi(red, nir):
    """Calculate NDVI."""
    return (nir - red) / (nir + red)

plt.imshow(ndvi(red, nir))
plt.colorbar()
~~~
{: .python}
![Matplotlib plot of calculated NDVI for the current landsat 8 scene](ndvi_integer_division.png)


The plot is filled with ``0``!  It turns out that the datatype of the input and output 
arrays is important, and both of the input rasters have pixel values that are
positive (unsigned) integers, which is also reflected in the array's numpy
dtypes.  This is probably leading to an integer division issue if we're using
python 2.  We can verify this hypothesis by checking the datatypes of both
the rasters and the resulting arrays.

~~~
    print gdal.GetDataTypeName(red_band.DataType), red.dtype
    print gdal.GetDataTypeName(nir_band.DataType), nir.dtype
~~~
{: .python}

    UInt16 uint16
    UInt16 uint16

Let's convert the input arrays to a floating-point dtype and calculate the NDVI once again.

~~~
import numpy as np

red = red.astype(np.float64)
nir = nir.astype(np.float64)

ndvi = ndvi(red, nir)
plt.imshow(ndvi, cmap='RdYlGn')
plt.colorbar()
~~~
{: .python}
![Matplotlib plot of calculated NDVI with invalid nodata areas for the current landsat 8 scene](ndvi_invalid_nodata_areas.png)

Looks like a reasonable output!

According to the [docs for Landsat 8](https://landsat.usgs.gov/collectionqualityband),
those blank areas around the edges should be ignored.  Many raster datasets
implement this with an optional **nodata value**.  If a nodata value is set,
then any pixel values that match it should be ignored.  It turns out that this
band doesn't have a defined nodata value.

~~~
# This band does not have a nodata value!
print red_band.GetNoDataValue()
~~~
{: .python}

    None

It turns out that we know from the docs that there's another landsat band
(``_BQA.TIF``) for our scene that contains extra metadata about the pixels of
the scene.  In this raster, any pixels with a value of ``1`` is filler and can
be ignored.

Let's create an NDVI array where:
* Any pixels marked as filler in the ``_BQA.TIF`` raster are set to ``-1``.
* Any pixels where the denominator is ``0`` is also set to ``-1``.

~~~
L8_QA_fn = '../data/LC08_L1TP_042034_20130605_20170310_01_T1_BQA_120x120.TIF'

import numpy as np

qa_ds = gdal.Open(L8_QA_fn)
qa_band = qa_ds.GetRasterBand(1)
qa = qa_band.ReadAsArray()

def ndvi_with_nodata(red, nir, qa):
    ndvi = (nir - red) / (nir + red)
    ndvi[qa == 1] = -1
    return ndvi
    
ndvi = ndvi_with_nodata(red, nir, qa)
plt.imshow(ndvi, cmap='RdYlGn')
plt.colorbar()
~~~
{: .python }
![Matplotlib plot with obviously specified nodata value](ndvi_with_nodata_value.png)

## 5. Save the NDVI Raster to Disk

Now, let's create an output geospatial raster and write our new NDVI values to it.

To do this, we need to tell GDAL which file format to use, if there are any
special options that should be set when the file is created, and what the
raster's dimensions should be.  We'll use the ``GTiff`` driver for this.
GeoTiff is an open format that is very well supported by GDAL and most GIS
applications.  (For a full list of supported formats, take a look at
``gdalinfo --formats``.)

~~~
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
new_band.WriteArray(ndvi)
~~~
{: .python}

Here's the equivalent code to write a raster with rasterio.  You can see that
both require the same information, but the way each library expresses the same
things is quite different.

~~~
with rasterio.open(L8_RED) as red_raster:
    source_crs = red_raster.crs
    source_transform = red_raster.transform

with rasterio.open('ndvi.tif', 'w', driver='GTIff',
                   height=ndvi.shape[0],    # numpy of rows
                   width=ndvi.shape[1],     # number of columns
                   count=1,                        # number of bands
                   dtype=rasterio.dtypes.float64,  # this must match the dtype of our array
                   crs=source_crs,
                   transform=source_transform) as ndvi_raster:
    ndvi_raster.write(ndvi, 1)  # optional second parameter is the band number to write to
    ndvi_raster.nodata = -1  # set the raster's nodata value
~~~
{: .python}

> ## Creating copies of datasets
>
> If we were looking to create a strict copy of one of our original GDAL
> datasets, we could call the much more abbreviated method
> ``driver.CreateCopy``.
>
> ~~~
> driver = gdal.GetDriverByName('GTiff')
> new_dataset = driver.CreateCopy('ndvi.tif', red_ds)
> ~~~
> {: .python}
>
> This is supported my many (but not all) of GDAL's drivers, and it assumes
> that the output dataset will have all of the same attributes as the current
> dataset.  In our case, we need a different datatype, so we use
> ``gdal.Create`` instead.
>
> The equivalent rasterio code is:
>
> ~~~
> rasterio.copy(L8_RED_fn, 'ndvi.tif')
> ~~~
> {: .python}
>
{: .callout}


And now that we've written out a new file, let's take a look at its
characteristics with one of the GDAL command-line utilities, ``gdalinfo``.
This utility is very useful for quickly displaying relevant information about a
raster without exploring its data.

~~~
!gdalinfo ndvi.tif
~~~
{: .shell}

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

## 6. Less Verbose Raster Calculators

### 6a. pygeoprocessing.raster_calculator

[``Pygeoprocessing``](http://pypi.python.org/pypi/pygeoprocessing) is a python
library developed by the [Natural Capital Project](http://naturalcapitalproject.org)
that offers open-source, computationally-efficient raster, vector and hydrological
routines for use in geoprocessing workflows.

One of the functions that pygeoprocessing provides is a 
[raster calculator][pygeoprocessing.raster_calculator], which will handle all
of the boilerplate code for opening the needed rasters,
creating the output raster, and handling input rasters in a
computationally-efficient manner.

The assumptions of this raster calculator are:
* The input rasters are assumed to be spatially aligned, but need only have the same dimensions.
* Input rasters must have the same block sizes.
* Any GDAL-readable format may be used for input rasters, but a GeoTiff will be written out.

~~~
# Note: this requires pygeoprocessing >= 0.4
import pygeoprocessing

# Here's the same NDVI function we defined earlier
def ndvi_with_nodata(red, nir, qa):
    ndvi = (nir - red) / (nir + red)
    ndvi[qa == 1] = -1
    return ndvi

pygeoprocessing.raster_calculator(
    [(L8_RED, 1), (L8_NIR, 1), (L8_QA, 1)],
    local_op=ndvi_with_nodata,
    target_raster_path='ndvi.tif',
    datatype_target=gdal.GDT_Float32,
    nodata_target=-1)  # we assume the output nodata value is -1 in our NDVI function
~~~
{: .python}

### 6b. gdal_calc.py

If you have the GDAL command-line utilities installed, you can also use the
provided python script to do raster calculation for you.  Like with the
pygeoprocessing approach, all your raster inputs are assumed to be aligned and
they must have the same dimensions.  This utility is only available from its
command-line interface.

~~~
gdal_calc.py \
    -A ../data/LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF \
    -B ../data/LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.TIF \
    -C ../data/LC08_L1TP_042034_20130605_20170310_01_T1_BQA_120x120.TIF \
    --outfile=ndvi_gdalcalc.tif \
    --type=Float64 \
    --overwrite \
    --calc="numpy.where(C == 1, -1, (A-B)/(A+B))"
~~~
{: .shell}


## 7. What about when your rasters are from different sources, with different projection, extent, resolution?

To be able to do raster math and have the outputs make sense, we may need do
some combination of reprojecting, resampling and clipping.  This can be done
with just GDAL, but there are several tools out there to help us with this
process.

> ## Warping directly with GDAL/rasterio
> 
> We won't cover GDAL and rasterio's low-level warping functionality, but documentation is available online if you're interested.
> * [``rasterio.warp.reproject``](https://mapbox.github.io/rasterio/topics/reproject.html) python API documentation
> * [``osgeo.gdal.ReprojectImage``](http://www.gdal.org/gdalwarper_8h.html#ad36462e8d5d34642df7f9ea1cfc2fec4) API documentation
> * [``gdalwarp``](http://www.gdal.org/gdalwarp.html) command-line interface to GDAL's warping functionality
> * ``rio warp`` (``rio warp --help``) command-line tool to rasterio's warping functionality
>
> Both ``pygeoprocessing`` and ``pygeotools`` have utilities to help automate
> the warping and aligning of stacks of inputs, and are generally easier to use
> than directly warping a single raster.
{: .callout}

### 7a. Mount Rainier DEM example - next episode

### 7b. Calculating Change in NDVI with Pygeoprocessing

How about if we want to calculate the change in NDVI between two different
landsat 8 scenes?  Here we have the same scene, both from June, but one is from
2013 and the other is from 2016.  They're already in the same projection, but
they are clearly misaligned.  Let's use pygeoprocessing to align and clip the
inputs so the match and then use ``pygeoprocessing.raster_calculator`` to
calculate the difference in NDVI between the two years.

|-------------------------------------------------------------------------------------------|
| Imperfect overlap between the same Landsat 8 scene from 2013 and 2016                     |
|-------------------------------------------------------------------------------------------|
| ![imperfect overlap between two years of the same Landsat 8 scene](imperfect_overlap.png) |
|-------------------------------------------------------------------------------------------|

~~~
# These are the paths to where we would like the aligned stack of inputs to be saved on disk.
al_red_2013 = 'red_2013.tif'
al_red_2016 = 'red_2016.tif'
al_nir_2013 = 'nir_2013.tif'
al_nir_2016 = 'nir_2016.tif'
al_qa_2013 = 'qa_2013.tif'
al_qa_2016 = 'qa_2016.tif'
aligned_rasters_list = [al_red_2013, al_nir_2013, al_qa_2013, al_red_2016, al_nir_2016, al_qa_2016]


red_2013_info = pygeoprocessing.get_raster_info(L8_RED_2013)

# align the stack of rasters
pygeoprocessing.align_and_resize_raster_stack(
    [L8_RED_2013, L8_NIR_2013, L8_QA_2013, L8_RED_2016, L8_NIR_2016, L8_QA_2016],
    aligned_rasters_list,
    ['nearest']*6,
    target_pixel_size=red_2013_info['pixel_size'],
    bounding_box_mode='intersection')

~~~
{: .python}

Once ``align_and_resize_raster_stack`` completes, all of the aligned raster
datasets have the same dimensions and resolution.  We can double-check this by
verifying that the raster's critical characteristics all match.

~~~
print set(str(pygeoprocessing.get_raster_info(filename)) for filename in aligned_rasters_list)
~~~

Now that our rasters are aligned, we can calculate the difference in NDVI rasters.

~~~
def diff_ndvi(red_2013, nir_2013, qa_2013, red_2016, nir_2016, qa_2016):
    # valid pixel stacks in this calculation are those where:
    #   * the QA raster for both Landsat scenes indicate that the pixels aren't fill
    #   * The denominator of the NDVI calculation isn't 0.
    # By indexing into each raster, we only perform our NDVI calculations on
    # stacks that we know are valid.
    valid_pixels = (qa_2013!=1) & (qa_2016!=1) & (red_2013+nir_2013 != 0) & (red_2016+nir_2016 != 0)

    def calc_ndvi(red, nir):
        red = red[valid_pixels].astype(numpy.float)
        nir = nir[valid_pixels].astype(numpy.float)
        return (nir - red) / (nir + red)

    ndvi_2013 = calc_ndvi(red_2013, nir_2013)
    ndvi_2016 = calc_ndvi(red_2016, nir_2016)

    ndvi = numpy.empty_like(red_2013, dtype=numpy.float32)
    ndvi[:] = -9999
    ndvi[valid_pixels] = ndvi_2016 - ndvi_2013
    return ndvi


pygeoprocessing.raster_calculator(
    [(al_red_2013, 1), (al_nir_2013, 1), (al_qa_2013, 1),
     (al_red_2016, 1), (al_nir_2016, 1), (al_qa_2016, 1)],
    diff_ndvi, 'diff_ndvi.tif', gdal.GDT_Float32, -9999)

pyplot.imshow(gdal.Open('diff_ndvi.tif').ReadAsArray(), cmap='RdYlGn')
pyplot.colorbar()
~~~
{: .python}

Pygeoprocessing also has a few routines that will help us to determine the mean change in NDVI per county.

~~~
# reproject the vector to the Raster's projection
reprojected_vector = 'ca_counties_utm11.shp'
pygeoprocessing.reproject_vector(
    'CA_counties/CA_counties.shp', red_2013_info['projection'],
    reprojected_vector)

# Aggregate ndvi by county name
stats = pygeoprocessing.zonal_statistics(
    ('diff_ndvi.tif', 1), reprojected_vector, 'NAME',
    polygons_might_overlap=False)

for county_name, aggregate_data in stats.iteritems():
    try:
        print county_name, aggregte_data['sum']/aggregate_data['count']
    except ZeroDivisionError:
        pass
~~~
{: .python}

    Mariposa   -0.0118313196727
    Fresno     -0.00661338400231
    Mono       -0.00920776345542
    Merced     0.00714124114347
    Madera     -0.00574486546421
    Tuolumne   0.00532270278817
    Inyo       -0.00188927021006
    Tulare     -0.00599385776893
    Alpine     0.0167325024718



[landsat8preview]: https://landsat-pds.s3.amazonaws.com/L8/042/034/LC80420342013156LGN00/LC80420342013156LGN00_thumb_small.jpg "Landsat 8 preview image over the California Central Valley"
[pygeoprocessing.raster_calculator]: http://pythonhosted.org/pygeoprocessing/packages/geoprocessing.html#pygeoprocessing.geoprocessing.raster_calculator
