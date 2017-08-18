import os

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy

cur_dir = os.path.dirname(__file__)

def render(filepath):
    """Visualize a blocksize of 536x15 from landcover.tif."""
    ds = gdal.Open(filepath)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray(win_xsize=536,
                             win_ysize=100)
    array.astype(numpy.float32)
    nodata = band.GetNoDataValue()

    ma_array = numpy.ma.masked_array(array, mask=array==nodata)
    plt.clf()  # clear figure
    plt.xticks([0, 535])
    plt.yticks(numpy.append(numpy.array([0]), numpy.arange(14, 99, 15)))
    plt.grid(color='b', linestyle='-', linewidth=1)
    plt.title('Blocksize: 536x15 (/data/landcover.tif)')
    plt.imshow(ma_array, origin='upper')

    out_png_name = os.path.join(cur_dir, 'landcover-blocks.png')
    if os.path.exists(out_png_name):
        os.remove(out_png_name)

    plt.savefig(out_png_name, dpi=150, bbox_inches='tight')

if __name__ == '__main__':
    render(os.path.join(os.path.dirname(__file__), '..', '..', 'docker',
                        'data', 'landcover.tif'))
