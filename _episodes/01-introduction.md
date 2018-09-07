---
title: "Setup Tutorial Python Environment"
teaching: 5
exercises: 0

questions:
- "How do I setup a Python environment to run examples in this tutorial?"

objectives:
- Create a conda environment with an environment definition file.

keypoints:
- It's best practice to create a unique conda environment for each of your projects. Here we install a raster environment called 'rasterenv'.
---

## Prerequisites:

This tutorial will use multiple Python packages to work with raster data. To set up a local ``conda`` environment, download [this conda environment
definition](https://raw.githubusercontent.com/geohackweek/tutorial_contents/master/raster/environment.yml) and create an environment like so:

~~~
$ conda env create -f environment.yml
$ source activate rasterenv
~~~
{: .shell}
