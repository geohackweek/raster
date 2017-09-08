---
title: "Geospatial Concepts: Raster Data"
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
- Some image formats have been adapted to store spatial metadata

---

# Images and Pixels

While vector graphics compose points, lines and polygons from defined vertices,
raster graphics are composed of a regular grid of measurements that have
numerical value.  We use raster graphics every day ... even the screen you're
reading this on implements raster graphics!  These two methods of representing
information, rasters and vectors, are complimentary, and each has their
advantages:

* Vector graphics are useful for storing data that has discrete boundaries,
  such as country borders, land parcels, and streets. [source](http://support.esri.com/en/other-resources/gis-dictionary/term/vector%20data%20model) 
* Raster graphics are useful for storing data that varies continuously, as in
  an aerial photograph, a satellite image, a surface of chemical
  concentrations, or an elevation surface. [source](http://support.esri.com/en/other-resources/gis-dictionary/term/raster%20data%20model)

In computer graphics, vector geometries are often rendered into raster images,
effectively taking a snapshot of the geometry from a defined
viewpoint.  This makes it near-trivial for our computer screens to display
complicated graphics scenes, by reducing the complexity, detail and
dimensionality down to a simple 2-D matrix.

Because of this snapshot quality of raster graphics, they are commonly used in
digital photography.  Take a look at these
three bands (red, green, and blue) from a Landsat 8 scene.  The image for each
band was taken by a different sensor on the Landsat satellite, and each band
contains a single value for each pixel.  Together, the values of these three
bands can be combined into an RGB image for display as a digital image.

|-----------------------------------|----------------------------------------|--------------------------------------|
| Red Band from a Landsat Scene     | Green Band from a Landsat Scene        | Blue Band from a Landsat Scene       |
|-----------------------------------|----------------------------------------|--------------------------------------|
|![Landsat 8: Red Band](L8_red.png) | ![Landsat 8: Green Band](L8_green.png) | ![Landsat 8: Blue Band](L8_blue.png) |
|-----------------------------------|----------------------------------------|--------------------------------------|

This is fundamentally a space-filling model, where all pixels have a value of some sort.

# What makes a raster geospatial?

A raster is just an image in sensor coordinates until we specify what part of the earth the
image covers.  This is done through two pieces of metadata that accompany the
pixel values of the image:

* **Coordinate Reference System** or "CRS". This specifies the mathematical
  model of the earth the image assumes.
* **Affine Geotransformation** This dicates the size, tilt and layout of the
  raster's pixels.  Defining this for the whole image allows the image's pixels
  to be referenced by local indices rather than global coordinates, and answers
  questions such as:
    * How much area does a given pixel cover?
    * Given the CRS, what is the origin?
    * In what direction does the raster "grow" as pixel indices increas?

Spatially-aware applications are careful to interpret this metadata
appropriately.  If we aren't careful (or are using a raster-editing application
that ignores spatial information), we can accidentlly strip this spatial
metadata.  Photoshop, for example, can edit GeoTiffs, but we'll lose the embedded
spatial metadata!

# Common Types of Raster Datasets

Unlike vector data, which can be points, lines, polygons, or combinations of
these types, raster datasets are structured into 2-dimensional arrays, where
each array element is a measurement value (e.g., brightness, temperature).  This is a convenient and concise way to
store and interact with collections of related measurements, arranged into a
grid, and is especially convenient now that we have reliable, high-resolution
digital photography that can be mounted to an aircraft or spacecraft.

Examples of common raster datasets:

* Raw, remotely sensed imagery from airborne or satellite sensors
* Processed and derived data products including
    * Orthorectified, multispectral imagery such as those acquired by [Landsat](https://landsat.usgs.gov) or [MODIS](https://modis.gsfc.nasa.gov) sensors
    * [Land-use/Land-cover products](https://www.mrlc.gov/nlcd2011.php) from classification of multispectral data
    * Digital Elevation Models (DEMs) such as [ASTER GDEM](https://asterweb.jpl.nasa.gov/gdem.asp)

# Limitations of the Raster Format
* Measurements are spatially arranged in a regular grid, which may not be an
  accurate representation of real-world phenomena.
* Space-filling model assumes that all pixels have value
* Changes in resolution can drastically change the meaning of a dataset's
  values.

