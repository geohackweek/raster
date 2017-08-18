# approximately what percentage area of yosemite national park is above 3500m (11482 ft.)?
import os

from osgeo import gdal
import pygeoprocessing

OUTPUT_DIR = '/shared/high_elevation_area'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

dem = os.path.join('/shared', 'grasslands_demo', 'joined_dem.tif')

# use iterblocks to calculate the within the park and the area above 3500m.
import time
start_time = time.time()
num_park_pixels = 0.
num_3500_pixels = 0.
for dem_info, dem_block in pygeoprocessing.iterblocks(dem):

    num_park_pixels += len(dem_block[dem_block != -1])
    num_3500_pixels += len(dem_block[(dem_block != -1) & (dem_block >= 3500)])

print 'Iterblocks took %ss' % (time.time() - start_time)
print 'Park pixels: %s' % num_park_pixels
print 'High-elevation pixels %s' % num_3500_pixels
print 'Percentage of park land above 3500m: %s%%' % round(
    (num_3500_pixels / num_park_pixels) * 100, 2)

# Compare iterblocks time with pure-numpy approach.
# Expected: This will be slightly faster than loading into memory, but not by
# much.  Real gains come when iterating over dataset too large to fit into main
# memory.
start_time = time.time()
dem_raster = gdal.Open(dem)
dem_array = dem_raster.ReadAsArray()
num_park_pixels = len(dem_array[dem_array != -1])
num_3500_pixels = len(dem_array[dem_array >= 3500])
print 'numpy took %ss' % (time.time() - start_time)
print 'Park pixels: %s' % num_park_pixels
print 'High-elevation pixels %s' % num_3500_pixels
print 'Percentage of park land above 3500m: %s%%' % round(
    (float(num_3500_pixels) / num_park_pixels) * 100, 2)

# Compare with aggregate_raster_values_uri
yosemite_vector = '/data/yosemite.shp'
stats = pygeoprocessing.aggregate_raster_values_uri(
    raster_uri=dem,
    shapefile_uri=yosemite_vector)

# Print the mean hight across the park
# 9999 is used as a Feature ID when we aggregate across the whole vector
print stats.pixel_mean[9999]
