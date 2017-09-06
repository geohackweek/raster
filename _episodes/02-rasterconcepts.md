---
title: "Geospatial Concepts: Raster Data"
teaching: 10
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

---

# Images and Pixels

* Bands (such as from images, e.g. R, G, B)
* Pixel values belong to individual bands

This is fundamentally a space-filling model, where all pixels have a value of some sort.


# What makes a raster geospatial?

Fundamentally, a raster is just an image until we specify what part of the earth the
image covers.  This is done through 

* Affine Geotransformation (this dicates the size, tilt and layout of the raster's pixels)
* Projection (this specifies the mathematical model of the earth the image assumes, among other things.)

# Common Types of Raster Datasets

e.g. LULC, DEM, climate data

# Categories of Operations for Raster Data

* Local operations (pixel-stack)
* Focal/Neighborhood operations (e.g. convolutions)
* Zonal operations (e.g. sum up all the pixels under this vector feature)
* Application-specific operations (e.g. hydrological routing)

# Limitations
* Space-filling model assumes that all pixels have value

