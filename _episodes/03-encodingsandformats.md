---
title: "Encodings, Formats and Libraries"
teaching: 10
exercises: 0

questions:
- "What sorts of formats are available for representing raster datasets?"

objectives:
- Understand the high-level data interchange formats for raster datasets.

keypoints:
- 

---

# File formats for raster datasets

* There are hundreds of standard file formats!
* Different libraries support various formats to differing degrees.
    * GDAL (Geospatial Data Abstrction Library) provides a consistent
      interface across lots of formats.  This broad compatibility has
      made it nearly ubiquitous, even across languages.
* Fundamentally, what makes a raster geospatial?  It's an image with some geospatial metadata attached to it.
    * The geospatial metadata isn't strictly necessary for geoprocessing, but it is important for representing where on earth the data are located.
* Virtual filesystems (GDAL-only)
* GDAL VRT format (GDAL-only)
* OGC web services


# Interchange formats between python objects

Different parts of a supported raster format are represented with different native python types.

* Pixel values: numpy arrays (fundamentally, this is the core of what is a raster!)
* Affine Geotransform: GDAL: 6-tuple/array, Rasterio: Affine object
* projection: string Well-Known Text representation

