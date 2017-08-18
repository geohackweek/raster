import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from osgeo import gdal
import numpy

cur_dir = os.path.dirname(__file__)

def render(filepath):
    """Visualize different pixel values from landcover.tif."""
    ds = gdal.Open(filepath)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray(win_xsize=100, win_ysize=50)
    array.astype(numpy.float32)
    nodata = band.GetNoDataValue()

    ma_array = numpy.ma.masked_array(array, mask=array==nodata)
    plt.clf()  # clear figure

    plt.xticks(size='small')
    plt.yticks(size='small')

    white_patch = patches.Patch(color='white', label='Nodata cells',
                                edgecolor='black')
    legend = plt.legend(handles=[white_patch])
    legend.get_frame().set_facecolor('#999999')

    plt.title('Pixel values in data/landcover.tif')
    plt.imshow(ma_array, origin='upper', interpolation='none')
    #plt.imshow(ma_array[100:350, 100:350], origin=(100,100),
    #           extent=(100, 350, 100, 350))
    plt.legend(loc='lower right', bbox_to_anchor=(0.55, -.75),
               fontsize='small')

    out_png_name = os.path.join(cur_dir, 'landcover-nodata.png')
    if os.path.exists(out_png_name):
        os.remove(out_png_name)

    plt.savefig(out_png_name, dpi=75, bbox_inches='tight')

if __name__ == '__main__':
    render(os.path.join(os.path.dirname(__file__), '..', '..', 'docker',
                        'data', 'landcover.tif'))
