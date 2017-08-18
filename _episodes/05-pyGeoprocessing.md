---
title: "Efficient raster computation with PyGeoProcessing"
teaching: 30 
exercises: 15
questions:
- "What problems can PyGeoProcessing address?"
- "When might PyGeoProcessing be helpful?"
objectives:
- "Understand how to execute a pygeoprocessing-style workflow"
- "Identify when and how PyGeoProcessing can benefit an analysis"
keypoints:
- "PyGeoProcessing provides programmable operations for efficient raster computations"
- "PyGeoProcessing is most useful for **large but not big** data"
- "PyGeoProcessing can help you to align inputs so they overlap perfectly"
- "If your rasters may be too large to fit into main memory, PyGeoProcessing may be faster than matrix operations"
---

# What is PyGeoProcessing?

![NatCap Logo](natcap-logo.png)
![InVEST Logo](invest-logo.png)
![PyGeoProcessing Logo](pygeoprocessing-logo.png)


* [PyGeoProcessing](https://bitbucket.org/richpsharp/pygeoprocessing) is a 
    python library of geospatial processing routines developed 
    and maintained by the Natural Capital Project (NatCap).
* Development began in 2011 as NatCap began migrating the [Integrated 
    Valutation of Ecosystem Services and Tradeoffs (InVEST)](http://naturalcapitalproject.org/invest)
    software to an open-source platform.
    * InVEST is a software tool that helps decision-makers understand tradeoffs
        in land-use and marine spatial planning decisions in terms of the benefits
        provided by nature ("Ecosystem Services")
    * Early versions of InVEST were free geoprocessing scripts based on ArcGIS
        * Quickly ran into limitations of the platform:
            * Difficult to batch-process lots of runs
            * Very difficult to link different models together
            * Model runs were very slow, sometimes taking days or weeks to run complex analyses
    * The first free, purely open-source InVEST models were released in 2011
    * Development of the new InVEST required a portable replacement of the
        geoprocessing routines required by the models, but none existed at the 
        time.
    * PyGeoProcessing evolved from this need, and was released as its own
        open-source project in 2015, announced at FOSS4G-NA.
* PyGeoProcessing is designed with the same functional requirements of InVEST:
    * Work within memory-constrained python environments (e.g. 32-bit python installations)
    * Support very large datasets on a local filesystem
    * Geoprocessing routines must be computationally efficient
* PyGeoProcessing is under active development, and is being continually improved

* **Key features**:
    * Programmable raster stack calculator
    * 2D Convolution with an arbitrary kernel
    * Euclidean Distance transform
    * Reclassification
    * D-infinity routing:
        * Stream network delineation
        * Distance to stream
        * Flow direction
        * Pixel export
        * watershed delineation
    * Helper functions for:
        * iterating over raster blocks
        * aligning and resampling stacks of rasters
        * extracting key raster metadata
        * Creating new raster datasets

> ## API Updates in Progress
> 
> We're actively working to improve pygeoprocessing, so the API examples you see here
> may change in the near future.
>
> API documentation can be found here: 
> [https://pythonhosted.org/pygeoprocessing/](https://pythonhosted.org/pygeoprocessing/)
{: .callout}



# What PyGeoProcessing can do for you

## When it makes sense to use PyGeoProcessing
* You need a reproducible workflow for your analysis
* Your analysis needs to be run many times (such as in optimization routines)
* Your data is accessible on a single computer ("*large* but not *big*")
* You have limited memory or are in a 32-bit programming environment
* Your program needs to be able to work with inputs that could be inconveniently large (won't fit into active memory)


## Why not just use GIS software?
* Most GIS installations are very large, and may break your script with each upgrade (ArcGIS is notorious for this)
* GIS don't always provide pure-python interfaces, or can't execute scripts from the command-line
* You can't ``pip install`` your GIS software


## Why not just use ``numpy`` directly on extracted matrices?
If you can, go for it!  PyGeoProcessing is best for cases where your data are large
enough that you cannot fit it all into main memory, for efficiently automating
complex workflows, and for common nontrivial operations.
It won't be relevent for every use case.

### Overhead of looping in python
Some operations that require a lot of looping, though, are especially challenging to
do in python.  In a python loop, every iteration needs to be able to handle all of the
possible types that a value might be.  For every line of python, at least 20 lines of C++
are executed.  This means that if your dataset is of any reasonable size and you need
to visit every pixel, you  may want to consider compiling a cython extension.

Consider this simple python function.

~~~
def foo():
    count = 0
    for i in xrange(100):
        count += i
~~~
{: .python}

Compare it with the [C code that must be executed](loop-overhead.html) to do
something this simple.  For this reason, you may need to compile your focal
operations to get them to run fast.

### Swapping Active Memory is Expensive

When arrays can't fit into active memory (but can stil be addressed), the Operating
System is left to swap chunks of memory to disk to make room for the parts of
active memory that are needed **right now**.  The chunks can then be loaded back 
into memory again later when they are needed.  This is convenient, but expensive,
since the OS can't predict what it will need next and has to wait until its needed.
For many analyses, this isn't an issue.

# Workflow Examples

## Single-output workflow: Steep, High-Elevation Grasslands in Yosemite

> ## Running this code within the docker image
> Since we're writing programs here that are most convenient to have within a file
> instead of within a python shell, it'll be most useful to run this program through
> the docker image from this tutorial.
>
> I'd recommend mounting your current workspace to ``/shared`` within the docker image.
>
> ~~~
> $ docker run -ti -v {path to your current workspace}:/shared geohackweek2016/rastertutorial:latest python /shared/{filename}.py
> ~~~
> {: .shell}
{: .callout}


~~~
import os
import logging
LOGGER = logging.getLogger('grasslands_demo')
logging.basicConfig(level=logging.INFO)

from osgeo import gdal
import pygeoprocessing

OUTPUT_DIR = '/shared/grasslands_demo'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
~~~
{: .python}

For this tutorial, we'll be making use of three rasters and one vector, 
all of which have already been projected ino a local coordinate system.

~~~
north_dem = '/data/N38W120.tif'
south_dem = '/data/N37W120.tif'
landcover = '/data/landcover.tif'
yosemite_vector = '/data/yosemite.shp'
~~~
{:.python}


### Joining our two DEMs

|----------------------------------|----------------------------------|
| ``/data/N38W120.tif``            | ``/data/N37W120.tif``            |
|----------------------------------|----------------------------------|
| ![DEM 1](../02-gdal/N38W120.png) | ![DEM 1](../02-gdal/N37W120.png) |
|----------------------------------|----------------------------------|
| ASTER GDEM is a product of METI and NASA.                           |
|---------------------------------------------------------------------|

Since both DEMs are projected already, we need to be a little more careful
about putting them together.

~~~
LOGGER.info('Merging DEMs')
import numpy
def _merge_dems(north_block, south_block):
    """Merge the two DEMs, picking the max value where overlap occurs."""
    valid_mask = (north_block != -1) | (south_block != -1)
    out_matrix = numpy.empty(north_block.shape)
    out_matrix[:] = -1
    out_matrix[valid_mask] = numpy.maximum(north_block[valid_mask],
                                           south_block[valid_mask])
    return out_matrix

pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[north_dem, south_dem],
    dataset_pixel_op=_merge_dems,
    dataset_out_uri=joined_dem,
    datatype_out=gdal.GDT_Int16,
    nodata_out=-1.0,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=30.0,
    bounding_box_mode='union',
    vectorize_op=False,
    aoi_uri=yosemite_vector,
)
~~~
{:.python}


![DEMs, clipped to yosemite outline](joined_dem.png)

### Calculate Slope

~~~
LOGGER.info('Calculating slope')
slope_raster = os.path.join(OUTPUT_DIR, 'slope.tif')
pygeoprocessing.calculate_slope(
    dem_dataset_uri=joined_dem,
    slope_uri=slope_raster)
~~~
{:.python}

![Visualization of slope of yosemite](slope.png)

### Locate Steep, High-Elevation Grasslands

~~~
lulc_nodata = pygeoprocessing.get_nodata_from_uri(lulc)
dem_nodata = pygeoprocessing.get_nodata_from_uri(joined_dem)
slope_nodata = pygeoprocessing.get_nodata_from_uri(slope_raster)

out_nodata = -1
def _find_grasslands(lulc_blk, dem_blk, slope_blk):
    # All blocks will be the same dimensions

    # Create a mask of invalid pixels due to nodata values
    valid_mask = ((lulc_blk != lulc_nodata) &
                  (dem_blk != dem_nodata) &
                  (slope_blk!= slope_nodata))

    # grasslands are lulc code 10
    matching_grasslands = ((lulc_blk[valid_mask] == 10) &
                           (slope_blk[valid_mask] >= 45) &
                           (dem_blk[valid_mask] >= 2000))

    out_block = numpy.empty(lulc_blk.shape)
    out_block[:] = 0
    out_block[~valid_mask] = out_nodata
    out_block[valid_mask] = matching_grasslands
    return out_block


pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[lulc, joined_dem, slope_raster],
    dataset_pixel_op=_find_grasslands,
    dataset_out_uri=os.path.join(OUTPUT_DIR, 'high_elev_steep_grasslands.tif'),
    datatype_out=gdal.GDT_Int16,
    nodata_out=out_nodata,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=pygeoprocessing.get_cell_size_from_uri(joined_dem),
    bounding_box_mode='intersection',
    vectorize_op=False,  # this will soon be required.
    aoi_uri=yosemite_vector)
~~~
{:.python}

![High elevation, steep grasslands](high_elev_steep_grasslands.png)


## Raster Analysis: Percentage of Yosemite above 3500m

Useful for: analyzing pixels inside of a raster or set of overlapping rasters.

``pygeoprocessing.iterblocks`` is a generator that on each iteration provides:

* A dict of contextual information (where the block is located within the raster)
* A numpy array of the block that was just loaded

~~~
import os

from osgeo import gdal
import pygeoprocessing

OUTPUT_DIR = '/shared/high_elevation_area'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# We'll use the DEM from the tutorial above.
dem = '/shared/grasslands_demo/joined_dem.tif'

num_park_pixels = 0.
num_3500_pixels = 0.
for dem_info, dem_block in pygeoprocessing.iterblocks(dem):

    num_park_pixels += len(dem_block[dem_block != -1])
    num_3500_pixels += len(dem_block[(dem_block != -1) & (dem_block >= 3500)])

print 'Percentage of park land above 3500m: %s%%' % round(
    (num_3500_pixels / num_park_pixels) * 100, 2)
~~~
{: .python}


## Zonal Statistics

``pygeoprocessing.aggregate_raster_values_uri`` allows us to collect statistics about
pixel values located underneath a vector.  If there are mulitple polygons in the vector,
stats will be aggregated for each polygon.

~~~
# Compare with aggregate_raster_values_uri
yosemite_vector = '/data/yosemite.shp'
stats = pygeoprocessing.aggregate_raster_values_uri(
    raster_uri=dem,
    shapefile_uri=yosemite_vector)


# Print the mean hight across the park
# 9999 is used as a Feature ID when we aggregate across the whole vector
print stats.pixel_mean[9999]
~~~
{: .python}

# Preparing a Stack of Rasters

It can be very useful to process a stack of rasters such that they align perfectly.
This is especially handy if we need to use these aligned rasters later on.

~~~
aligned_dir= '/shared/alignment_demo'
if not os.path.exists(aligned_dir)
pygeoprocessing.align_dataset_list(
    dataset_uri_list=[landcover, dem],
    dataset_out_uri_list=[
        os.path.join(aligned_dir, 'landcover_aligned.tif'),
        os.path.join(aligned_dir, 'dem_aligned.tif')],
    resample_method_list=['nearest', 'nearest'],
    out_pixel_size=pygeoprocessing.get_cell_size_from_uri(dem),
    mode='intersection',
    dataset_to_align_index=0
)
~~~

> ## Exercise: What's the mean elevation of evergreen forest in Yosemite?
> 
> There are several ways to do this.  The key is getting the LULC and the
> DEM rasters to the same shape and resolution.
>
> ### Approach #1: ``vectorize_datasets`` and ``aggregate_raster_values_uri``
> ~~~
> import os
> 
> import pygeoprocessing
> import numpy
> from osgeo import gdal
> 
> def _dem_values_under_evergreen_forest(lulc_block, dem_block):
>     out_matrix = numpy.empty(lulc_block.shape)
>     out_matrix[:] = -1
>     matching_landcover_mask = lulc_block == 1
>     out_matrix[matching_landcover_mask] = dem_block[matching_landcover_mask]
>     return out_matrix
> 
> 
> out_path = '/shared/mean_elevation_exercise/matching_pixels.tif'
> out_dir = os.path.dirname(out_path)
> if not os.path.exists(out_dir):
>     os.makedirs(out_dir)
> 
> dem_path = '/shared/grasslands_demo/joined_dem.tif'
> pygeoprocessing.vectorize_datasets(
>     dataset_uri_list=['/data/landcover.tif', dem_path],
>     dataset_pixel_op=_dem_values_under_evergreen_forest,
>     dataset_out_uri=out_path,
>     datatype_out=gdal.GDT_Int16,
>     nodata_out=-1,
>     pixel_size_out=pygeoprocessing.get_cell_size_from_uri(dem_path),
>     bounding_box_mode='intersection')
> 
> stats = pygeoprocessing.aggregate_raster_values_uri(
>     out_path, '/data/yosemite.shp')
> 
> print stats.pixel_mean[9999]
> ~~~
> {: .python}
>
>
> ### Approach #2: ``align_dataset_list`` and ``iterblocks``
>
> ~~~
> aligned_lulc = os.path.join(out_dir, 'aligned_lulc.tif')
> aligned_dem = os.path.join(out_dir, 'aligned_dem.tif')
> pygeoprocessing.align_dataset_list(
>     datset_uri_list=['/data/landcover.tif', dem_path],
>     dataset_out_uri_list=[aligned_lulc, aligned_dem],
>     resample_method_list=['nearest', 'nearest'],
>     out_pixel_size=pygeoprocessing.get_cell_size_from_uri(dem_path),
>     mode='intersection',
>     dataset_to_align_index=0)
> 
> pixel_sum = 0.
> pixel_count = 0.
> for (lulc_data, lulc_block), (dem_data, dem_block) in itertools.izip(
>         pygeoprocessing.iterblocks(aligned_lulc),
>         pygeoprocessing.iterblocks(aligned_dem)):
>     matching_dem_cells = dem_block[lulc_data == 1]
>     pixel_sum += matching_dem_cells.sum()
>     pixel_count += len(matching_dem_cells)
> print pixel_sum / pixel_count
> ~~~
> {: .python}
{: .challenge}

