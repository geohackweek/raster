---
title: "Introduction: Working with Raster Data"
teaching: 5
exercises: 0

questions:
- "What is a raster?"
- "What sorts of information does a raster typically model?"
- "What are the major charateristics of a raster dataset?"
- "What assumptions does the format imply?"

objectives:
- Understand the raster data model

keypoints:
- Gridded data that vary in space and time are common in many geospatial applcations
- Specialized tools are needed to accommodate the complexity and size of many raster datasets
- GIS tools (e.g. QGIS, SAGA GIS) are usually needed to visualize these datasets

---
# Overview:

Scientists working with spatial data often need to manipulate datasets structured as arrays.  A common example is in working with hydrological modelling (e.g. where will water flow in a storm event?) using topographical data gathered from the US Geological Survey, or based on aerial or lidar photography gathered from a plane flying below the clouds.

# Common types of Geospatial data

* Raw multispectral datasets from data providers such as NASA, USGS and the like
* Classified Land-use / Land-cover datasets
* Digital Elevation Models
* Digital Orthoimages

Remote sensing is a major source for raster graphics.

# Characteristics of a Raster:

## Data Model

Rasters use a space-filling model, where all geographic features are represented
by discreet cells, arranged in a specific sequence.  Geospatial raster datasets
are effectively matrices with additional metadata to show which part of the 
planet the dataset represents.

#### Bands

Bands are layers of values that overlap perfectly.  Depending on the source of your 
raster and the information it represents, you may have multiple bands with numeric values that represent 
different things.  A DEM might have a single band where values represent the 
height of a pixel relative to sea level.  Or you could use a georeferenced 
natural-color aerial photograph using three bands, one each for Red, Green, and Blue.
Raw LANDSAT data contains several other bands as well:

|-------------------------------------------------------------------------------------|
| Bands of LANDSAT Thematic Mapper (TM) imagery                                       |
|-------------------------------------------------------------------------------------|
| ![Graphic labelling six bands of LANDSAT aerial photography](landsat_bands_all.gif) |
|-------------------------------------------------------------------------------------|
| Source: [NASA](https://svs.gsfc.nasa.gov/stories/Landsat/landsat_data.html)         |
|-------------------------------------------------------------------------------------|


#### NoData Value

Since raster datasets use a space-filling model, every pixel has a value.
Where pixel values should not have a value, a **Nodata Value** is used to indicate
a lack of information in a pixel.  Visually, this is often represented in GIS as
transparency.

|------------------------------------------------------------------------------------------|
| NW corner of /data/landcover.tif                                                         |
|------------------------------------------------------------------------------------------|
| ![Northwest corner os sample landcover raster demonstrating nodata](landcover-nodata.png)|
|------------------------------------------------------------------------------------------|


#### Coordinate Reference System

Raster datasets are fundamentally images, where each pixel has a value.  The spatial element of this dataset, however, lies in its Coordinate Reference System (CRS).  Here's an example CRS, represented as <a href="https://en.wikipedia.org/wiki/Well-known_text">Well-Known text </a>:

{% highlight text %}
PROJCS["WGS 84 / UTM zone 11N",                         # Name of the projected coordinate system
    GEOGCS["WGS 84",                                    # Geographic coordinate system
        DATUM["WGS_1984",                               # The datum (mathematical shape of the earth)
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],                  # Specific projection
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-117],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32611"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH

{% endhighlight %}

This collection of numbers and standards describes how to transform the
3-dimensional surface of the earth into a 2-dimensional image.  Getting 
projections right is a tricky business, and one that can take a great deal of 
expertise. ASTER DEMs come in the WGS84 geographic coordinate system, but are 
unprojected.  The datasets included in this tutorial are projected into UTM 
zone 11N.

The projection you choose can make a very big difference in the display of
information.  Here's an ASTER DEM from the Sierra Nevada mountains in 
California with different projections:

|---------------------------------------------------|-----------------------------------------------------|----------------------------------------------------|
| Unprojected                                       | Projected in UTM Zone 11N                           | Projected in North Pole LAEA Alaska                |
|---------------------------------------------------|-----------------------------------------------------|----------------------------------------------------|
| ![Unprojected DEM](ASTER-N37W120-unprojected.png) | ![UTM zone 11N](ASTER-N37W120-UTM11N.png)           | ![North Pole LAEA](ASTER-N37W120-northpole.png)    |
|---------------------------------------------------|-----------------------------------------------------|----------------------------------------------------|

#### Affine GeoTransform
Unfortunately, the CRS by itself is not enough to place the raster on the 
planet.  To do this, we need the Affine Geotransform, which allows us to map 
pixel coordinates into georeferenced space.

    GT = (233025.03117445827, 30.0, 0.0, 4210078.842723392, 0.0, -30.0)
    Xgeo = GT(0) + Xpixel*GT(1) + Yline*GT(2)
    Ygeo = GT(3) + Xpixel*GT(4) + Yline*GT(5)

Note that this significantly affects how pixels are arranged in space.  'Up'
could be either an increase or decrease in the row index, depending on the 
geotransform, and the image could be rotated.

Many raster datasets have square or near-square pixels as well, but this is not a
strict requirement.  The geotransform can support rectangular pixels of arbitrary size.

### Challenges with handling geospatial data

* Projections warp information, can lead to inaccuracies
* Size of raster data can be challenging to work around in a program
