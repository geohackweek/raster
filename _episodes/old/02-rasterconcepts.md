---
title: "Introduction to Raster Data"
teaching: 5
exercises: 0

questions:
- "What is a raster?"
- "What sorts of information does a raster typically model?"
- "What are the major characteristics of a raster dataset?"
- "What assumptions does the format imply?"

objectives:
- Understand the raster data model

keypoints:
- Gridded data that vary in space and time are common in many geospatial applications
- Specialized tools are needed to accommodate the complexity and size of many raster datasets
- Some image formats have been adapted to store spatial metadata

---

# What is a raster?

Unlike vectors, where features have discrete boundaries (which is useful for
storing data like country borders, land parcels, streets, or sample sites), rasters are
useful for storing data that varies continuously.  At its heart, a raster is:

* A dataset with measurements making up a rectangular grid of values.
* (Sometimes) multiple 2-dimensional arrays of values that overlap perfectly and
  portray slightly different characteristics of the same dataset.  We call
  these **bands**.

In the 1950's raster graphics were noted as a faster and cheaper (but
lower-resolution) alternative to vector graphics.

|-----------------------------------------------------------------------|
| Bands in Landsat 7 (bottom row of rectangles) and Landsat 8 (top row) |
|-----------------------------------------------------------------------|
| <img src="ETM+vOLI-TIRS-web_Feb20131.jpg" style="width: 1000px;"/>    |
|-----------------------------------------------------------------------|
| Graphic created by L.Rocchio & J.Barsi.                               |
|-----------------------------------------------------------------------|


|---------------------------------------|----------------------------------------|----------------------------------------|
| Landsat 8 Band 1 ("Ultra Blue")       | Landsat 8 Band 3 ("Green")             | Landsat 8 Band 9 ("Cirrus")            |
|---------------------------------------|----------------------------------------|----------------------------------------|
|![Landsat 8: Ultra Blue](L8_band1.png) | ![Landsat 8: Green Band](L8_green.png) | ![Landsat 8: Blue Band](L8_cirrus.png) |
|---------------------------------------|----------------------------------------|----------------------------------------|


# What makes a raster geospatial?

A raster is just an image in local pixel coordinates until we specify what part
of the earth the image covers.  This is done through two pieces of metadata
that accompany the pixel values of the image:

* **Coordinate Reference System** or "CRS". This specifies the mathematical
  model of the earth the image assumes.
* **Affine Geotransformation** This dictates the size, tilt and layout of the
  raster's pixels.  Defining this for the whole image allows the image's pixels
  to be referenced by a local array index rather than global coordinates, and answers
  questions such as:
    * How much area does a given pixel cover?
    * Given the CRS, what is the origin?
    * In what direction does the raster "grow" as pixel indices increase?

Spatially-aware applications are careful to interpret this metadata
appropriately.  If we aren't careful (or are using a raster-editing application
that ignores spatial information), we can accidentally strip this spatial
metadata.  Photoshop, for example, can edit GeoTiffs, but we'll lose the embedded
CRS and geotransform!

# Common types of raster datasets

Examples of common raster datasets include:

* Raw, remotely sensed imagery from airborne or satellite sensors
* Processed and derived data products including
    * Orthorectified, multispectral imagery such as those acquired by [Landsat](https://landsat.usgs.gov) or [MODIS](https://modis.gsfc.nasa.gov) sensors
    * [Land-use/Land-cover products](https://www.mrlc.gov/nlcd2011.php) from classification of multispectral data
    * Digital Elevation Models (DEMs) such as [ASTER GDEM](https://asterweb.jpl.nasa.gov/gdem.asp)

# Limitations of the raster format
* Measurements are spatially arranged in a regular grid, which may not be an
  accurate representation of real-world phenomena.
* Space-filling model assumes that all pixels have value
* Changes in resolution can drastically change the meaning of values in a dataset

# Further reading

* There is a lot of material out there describing rasters. Here is another great lesson that uses a software carpentry template: [https://datacarpentry.org/organization-geospatial/01-intro-raster-data/index.html](https://datacarpentry.org/organization-geospatial/01-intro-raster-data/index.html)
