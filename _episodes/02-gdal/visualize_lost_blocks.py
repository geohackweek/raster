import os

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from osgeo import gdal
import numpy

cur_dir = os.path.dirname(__file__)

def render(filepath):
    """Visualize a blocksize of 536x15 from landcover.tif."""
    ds = gdal.Open(filepath)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray(win_ysize=500)
    array.astype(numpy.float32)
    nodata = band.GetNoDataValue()

    ma_array = numpy.ma.masked_array(array, mask=array==nodata)
    plt.clf()  # clear figure

    axis = plt.gca()
    axis.add_patch(
        patches.Rectangle(
            (0,100),
            3046,
            350,
            fill=True,  # remove background
            alpha=0.6,
            label='Blocks read in (blocksize=3046x1)',
            color='r'
        )
    )
    axis.add_patch(
        patches.Rectangle(
            (100, 100),
            350,
            350,
            fill=False,  # remove background
            alpha=0.7,
            label='Values kept',
            hatch='/',
            color='k'
        )
    )
    plt.xticks(size='small')
    plt.yticks(size='small')

    plt.title('Extracting 250x250 matrix from /data/N37W120.tif')
    plt.imshow(ma_array, origin='upper')
    #plt.imshow(ma_array[100:350, 100:350], origin=(100,100),
    #           extent=(100, 350, 100, 350))
    plt.legend(loc='lower right', bbox_to_anchor=(0.55, -.75),
               fontsize='small')

    out_png_name = os.path.join(cur_dir, 'N37W120-read-blocks.png')
    if os.path.exists(out_png_name):
        os.remove(out_png_name)

    plt.savefig(out_png_name, dpi=150, bbox_inches='tight')

if __name__ == '__main__':
    render(os.path.join(os.path.dirname(__file__), '..', '..', 'docker',
                        'data', 'N37W120.tif'))
