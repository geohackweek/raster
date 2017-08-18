
import glob
import os
import sys

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy


def render_as_png(filepath):
    ds = gdal.Open(filepath)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    nodata = band.GetNoDataValue()

    ma_array = numpy.ma.masked_array(array, mask=array==nodata)
    plt.clf()  # clear figure

    # make discreet colormap
    cm = plt.cm.get_cmap()
    color_list = cm(numpy.linspace(0, 1, 16))
    colormap_name = cm.name + ' LULC'
    discrete_cm = cm.from_list(colormap_name, color_list, 17)

    plt.imshow(ma_array, origin='upper', cmap=discrete_cm)
    colorbar = plt.colorbar()
    colorbar.set_ticks(numpy.arange(0, 17, 1))
    plt.clim(-0.5, 16.5)
    colorbar.set_ticklabels([
        '0: Water',
        '1: Evergreen Needle leaf Forest',
        '2: Evergreen Broadleaf Forest',
        '3: Deciduous Needle leaf Forest',
        '4: Deciduous Broadleaf Forest',
        '5: Mixed Forests',
        '6: Closed Shrublands',
        '7: Open Shrublands',
        '8: Woody Savannas',
        '9: Savannas',
        '10: Grasslands',
        '11: Permanent Wetland',
        '12: Croplands',
        '13: Urban and Built-Up',
        '14: Cropland/Natural Vegetation Mosaic',
        '15: Snow and Ice',
        '16: Barren or Sparsely Vegetated',
    ])


    base_filename = os.path.splitext(os.path.basename(filepath))[0]
    out_png_name = base_filename + '.png'
    if os.path.exists(out_png_name):
        os.remove(out_png_name)

    plt.savefig(out_png_name, dpi=100, bbox_inches='tight')

    # Add landcover classification labels to landcover
    # 0	    Water
    # 1	    Evergreen Needle leaf Forest
    # 2	    Evergreen Broadleaf Forest
    # 3	    Deciduous Needle leaf Forest
    # 4	    Deciduous Broadleaf Forest
    # 5	    Mixed Forests
    # 6	    Closed Shrublands
    # 7	    Open Shrublands
    # 8	    Woody Savannas
    # 9	    Savannas
    # 10	Grasslands
    # 11	Permanent Wetland
    # 12	Croplands
    # 13	Urban and Built-Up
    # 14	Cropland/Natural Vegetation Mosaic
    # 15	Snow and Ice
    # 16	Barren or Sparsely Vegetated




if __name__ == '__main__':
    filename = os.path.join(os.path.dirname(__file__), '..', '..', 'docker',
                            'data', 'landcover.tif')
    render_as_png(filename)
