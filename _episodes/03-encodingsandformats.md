---
title: "Encodings, Formats and Libraries"
teaching: 5
exercises: 0
questions:
- "What sorts of formats are available for representing raster datasets?"

objectives:
- Understand the high-level data interchange formats for raster datasets.

keypoints:
- Geospatial libraries such as GDAL are very useful for reading, writing and
  transforming rasters
- Once a raster's pixel values have been extracted to a NumPy array, they can
  be processed with more specialized libraries and routines.

---

# Libraries and File formats for raster datasets

[GDAL](http://gdal.org) (Geospatial Data Abstraction Library) is the de facto standard library for
interaction and manipulation of geospatial raster data.  The primary purpose of GDAL or a
GDAL-enabled library is to read, write and transform geospatial datasets in a
way that makes sense in the context of its spatial metadata.  GDAL also includes
a set of [command-line utilities](http://www.gdal.org/gdal_utilities.html) (e.g., gdalinfo, gdal_translate)
for convenient inspection and manipulation of raster data.

Other libraries also exist (we'll introduce rasterio in the next section of this
tutorial, and even more exist in the fields of geoprocessing (which would
include hydrological routing and other routines needed for Earth Systems
Sciences) and digital signal processing (including image classification,
pattern recognition, and feature extraction).

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

GDAL can operate on local files or even read files from the web like so:
~~~
$ SERVER='http://landsat-pds.s3.amazonaws.com/c1/L8/042/034/LC08_L1TP_042034_20170616_20170629_01_T1'
$ IMAGE='LC08_L1TP_042034_20170616_20170629_01_T1_B4.TIF'
$ gdalinfo /vsicurl/$SERVER/$IMAGE
~~~
{: .shell}
  Driver: GTiff/GeoTIFF
  Files: /vsicurl/http://landsat-pds.s3.amazonaws.com/c1/L8/042/034/LC08_L1TP_042034_20170616_20170629_01_T1/LC08_L1TP_042034_20170616_20170629_01_T1_B4.TIF
         /vsicurl/http://landsat-pds.s3.amazonaws.com/c1/L8/042/034/LC08_L1TP_042034_20170616_20170629_01_T1/LC08_L1TP_042034_20170616_20170629_01_T1_B4.TIF.ovr
         /vsicurl/http://landsat-pds.s3.amazonaws.com/c1/L8/042/034/LC08_L1TP_042034_20170616_20170629_01_T1/LC08_L1TP_042034_20170616_20170629_01_T1_MTL.txt
  Size is 7821, 7951
  Coordinate System is:
  PROJCS["WGS 84 / UTM zone 11N",
      GEOGCS["WGS 84",
          DATUM["WGS_1984",
              SPHEROID["WGS 84",6378137,298.257223563,
                  AUTHORITY["EPSG","7030"]],
              AUTHORITY["EPSG","6326"]],
          PRIMEM["Greenwich",0,
              AUTHORITY["EPSG","8901"]],
          UNIT["degree",0.0174532925199433,
              AUTHORITY["EPSG","9122"]],
          AUTHORITY["EPSG","4326"]],
      PROJECTION["Transverse_Mercator"],
      PARAMETER["latitude_of_origin",0],
      PARAMETER["central_meridian",-117],
      PARAMETER["scale_factor",0.9996],
      PARAMETER["false_easting",500000],
      PARAMETER["false_northing",0],
      UNIT["metre",1,
          AUTHORITY["EPSG","9001"]],
      AXIS["Easting",EAST],
      AXIS["Northing",NORTH],
      AUTHORITY["EPSG","32611"]]
  Origin = (204285.000000000000000,4268115.000000000000000)
  Pixel Size = (30.000000000000000,-30.000000000000000)
  Metadata:
    AREA_OR_POINT=Point
    METADATATYPE=ODL
  Image Structure Metadata:
    COMPRESSION=DEFLATE
    INTERLEAVE=BAND
  Corner Coordinates:
  Upper Left  (  204285.000, 4268115.000) (120d23'29.18"W, 38d30'44.39"N)
  Lower Left  (  204285.000, 4029585.000) (120d17'44.96"W, 36d21'57.41"N)
  Upper Right (  438915.000, 4268115.000) (117d42' 3.98"W, 38d33'33.76"N)
  Lower Right (  438915.000, 4029585.000) (117d40'52.67"W, 36d24'34.20"N)
  Center      (  321600.000, 4148850.000) (119d 1' 2.61"W, 37d28' 9.59"N)
  Band 1 Block=512x512 Type=UInt16, ColorInterp=Gray
    Overviews: 2607x2651, 869x884, 290x295, 97x99

This is very convenient to download files, but perhaps you want them in a
different file format:
~~~
$ gdal_translate -of VRT /vsicurl/$SERVER/$IMAGE LC08_L1TP_042034_20170616_20170629_01_T1_B4.vrt
~~~

Or maybe you want a subset of the file in a different coordinate system:
~~~
$ gdalwarp -t_srs EPSG:4326 -of VRT /vsicurl/$SERVER/$IMAGE LC08_L1TP_042034_20170616_20170629_01_T1_B4-wgs84.vrt
~~~

As you can see, there is a lot you can do with GDAL command line utilities!


# Programming Model: NumPy arrays

Because rasters are images, they are best thought of as 2-dimensional arrays.  If we
have multiple bands, we could think of an image as a 3-dimensional array.
Either way, we are working with arrays (matrices) of pixel values, which in the
python programming language are best represented by [NumPy](http://numpy.org) arrays.

For this tutorial, we'll perform basic operations with NumPy arrays extracted
from geospatial rasters.  For more information about multidimensional array
analysis, take a look at Thursday's tutorial on
[N-Dimensional Arrays](https://geohackweek.github.io/nDarrays).
