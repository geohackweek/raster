"""Locate all grasslands above 2000m within 300m of a stream."""
import logging
LOGGER = logging.getLogger('grasslands_demo')
logging.basicConfig(level=logging.INFO)

from osgeo import gdal
import pygeoprocessing

# First, let's determine the stream network.
# To do this, we need to mosaic the DEM and reproject to the local projection

import os

OUTPUT_DIR = '/shared/grasslands_demo'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

north_dem = '/data/N38W120.tif'
south_dem = '/data/N37W120.tif'

joined_dem = os.path.join(OUTPUT_DIR, 'joined_dem.tif')

yosemite_vector = '/data/yosemite.shp'
LOGGER.info('Starting union of DEMs')

import numpy
def _merge_dems(north_block, south_block):
    valid_mask = (north_block != -1) | (south_block != -1)
    out_matrix = numpy.empty(north_block.shape)
    out_matrix[:] = -1
    out_matrix[valid_mask] = numpy.maximum(north_block[valid_mask],
                                           south_block[valid_mask])
    return out_matrix

LOGGER.info('Merging DEMs')
pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[north_dem, south_dem],
    dataset_pixel_op=_merge_dems,
    dataset_out_uri=joined_dem,
    datatype_out=gdal.GDT_Int16,
    nodata_out=-1.0,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=30.0,
    bounding_box_mode='union',
    vectorize_op=False,
    aoi_uri=yosemite_vector,
)

# Next we need to calculate the slope layer.
LOGGER.info('Calculating slope')
slope_raster = os.path.join(OUTPUT_DIR, 'slope.tif')
pygeoprocessing.calculate_slope(
    dem_dataset_uri=joined_dem,
    slope_uri=slope_raster)

# OK!  Now we add it all together with a call to vectorize_datasets
LOGGER.info('Finding high-elevation, steep grasslands')
lulc = '/data/landcover.tif'

# segfault if I do this: gdal.Open(lulc).GetRasterBand(1).GetNoDataValue()
lulc_nodata = pygeoprocessing.get_nodata_from_uri(lulc)
dem_nodata = pygeoprocessing.get_nodata_from_uri(joined_dem)
slope_nodata = pygeoprocessing.get_nodata_from_uri(slope_raster)

out_nodata = -1
def _find_grasslands(lulc_blk, dem_blk, slope_blk):
    # All blocks will be the same dimensions

    # Create a mask of invalid pixels due to nodata values
    valid_mask = ((lulc_blk != lulc_nodata) &
                  (dem_blk != dem_nodata) &
                  (slope_blk!= slope_nodata))

    # grasslands are lulc code 10
    matching_grasslands = ((lulc_blk[valid_mask] == 10) &
                           (slope_blk[valid_mask] >= 45) &
                           (dem_blk[valid_mask] >= 2000))

    out_block = numpy.empty(lulc_blk.shape)
    out_block[:] = 0
    out_block[~valid_mask] = out_nodata
    out_block[valid_mask] = matching_grasslands
    return out_block


def _find_grasslands_pixels(lulc_pixel, dem_pixel, slope_pixel):
    if any(lulc_pixel == lulc_nodata,
           dem_pixel == dem_nodata,
           slope_pixel == slope_nodata):
        return out_nodata
    elif all(lulc_pixel == 10,
             slope_pixel >= 20,
             dem_pixel >= 2000):
        return 1
    return 0


pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[lulc, joined_dem, slope_raster],
    dataset_pixel_op=_find_grasslands,
    dataset_out_uri=os.path.join(OUTPUT_DIR, 'high_elev_steep_grasslands.tif'),
    datatype_out=gdal.GDT_Int16,
    nodata_out=out_nodata,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=pygeoprocessing.get_cell_size_from_uri(joined_dem),
    bounding_box_mode='intersection',
    vectorize_op=False,  # we
    aoi_uri=yosemite_vector)
