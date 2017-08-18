import os

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy
import pygeoprocessing

CUR_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CUR_DIR, '..', '..', 'docker', 'data')


def render(filepath, title, out_filename):
    ds = gdal.Open(filepath)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    array.astype(numpy.float32)
    nodata = band.GetNoDataValue()

    ma_array = numpy.ma.masked_array(array, mask=array==nodata)
    plt.clf()  # clear figure

    plt.xticks(size='small')
    plt.yticks(size='small')

    plt.title(title)
    plt.imshow(ma_array, origin='upper', interpolation='none')
    #plt.imshow(ma_array[100:350, 100:350], origin=(100,100),
    #           extent=(100, 350, 100, 350))
    plt.legend(loc='lower right', bbox_to_anchor=(0.55, -.75),
               fontsize='small')

    if os.path.exists(out_filename):
        os.remove(out_filename)

    plt.savefig(out_filename, dpi=75, bbox_inches='tight')

if __name__ == '__main__':
    unproj_dem = os.path.join(DATA_DIR, 'ASTGTM2_N37W120_dem.tif')
    render(unproj_dem,
           'ASTER N37W120 (unprojected)',
           'ASTER-N37W120-unprojected.png')

    render(os.path.join(DATA_DIR, 'N37W120.tif'),
           'ASTER N37W120 (UTM zone 11N)',
           'ASTER-N37W120-UTM11N.png')

    alaska_srs = """PROJCS["WGS 84 / North Pole LAEA Alaska",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
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
    PROJECTION["Lambert_Azimuthal_Equal_Area"],
    PARAMETER["latitude_of_center",90],
    PARAMETER["longitude_of_center",-150],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","3572"],
    AXIS["X",UNKNOWN],
    AXIS["Y",UNKNOWN]]"""

    out_filename = 'ASTER_alaska.tif'
    pygeoprocessing.reproject_dataset_uri(
        original_dataset_uri=unproj_dem,
        pixel_spacing=30,
        output_wkt=alaska_srs,
        resampling_method='nearest',
        output_uri=out_filename)
    render(out_filename,
           'ASTER N37W120 (North Pole LAEA Alaska)',
           'ASTER-N37W120-northpole.png')
