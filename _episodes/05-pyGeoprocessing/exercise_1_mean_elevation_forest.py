import os

import pygeoprocessing
import numpy
from osgeo import gdal

def _dem_values_under_evergreen_forest(lulc_block, dem_block):
    out_matrix = numpy.empty(lulc_block.shape)
    out_matrix[:] = -1
    matching_landcover_mask = lulc_block == 1
    out_matrix[matching_landcover_mask] = dem_block[matching_landcover_mask]
    return out_matrix


out_path = '/shared/mean_elevation_exercise/matching_pixels.tif'
out_dir = os.path.dirname(out_path)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

dem_path = '/shared/grasslands_demo/joined_dem.tif'
pygeoprocessing.vectorize_datasets(
    dataset_uri_list=['/data/landcover.tif', dem_path],
    dataset_pixel_op=_dem_values_under_evergreen_forest,
    dataset_out_uri=out_path,
    datatype_out=gdal.GDT_Int16,
    nodata_out=-1,
    pixel_size_out=pygeoprocessing.get_cell_size_from_uri(dem_path),
    bounding_box_mode='intersection')

stats = pygeoprocessing.aggregate_raster_values_uri(
    out_path, '/data/yosemite.shp')

print stats.pixel_mean[9999]

################

aligned_lulc = os.path.join(out_dir, 'aligned_lulc.tif')
aligned_dem = os.path.join(out_dir, 'aligned_dem.tif')
pygeoprocessing.align_dataset_list(
    datset_uri_list=['/data/landcover.tif', dem_path],
    dataset_out_uri_list=[aligned_lulc, aligned_dem],
    resample_method_list=['nearest', 'nearest'],
    out_pixel_size=pygeoprocessing.get_cell_size_from_uri(dem_path),
    mode='intersection',
    dataset_to_align_index=0)

pixel_sum = 0.
pixel_count = 0.
import itertools
for (lulc_data, lulc_block), (dem_data, dem_block) in itertools.izip(
        pygeoprocessing.iterblocks(aligned_lulc),
        pygeoprocessing.iterblocks(aligned_dem)):
    matching_dem_cells = dem_block[lulc_data == 1]
    pixel_sum += matching_dem_cells.sum()
    pixel_count += len(matching_dem_cells)
print pixel_sum / pixel_count
