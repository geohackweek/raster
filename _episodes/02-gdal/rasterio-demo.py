import os
import rasterio

with rasterio.open('/data/landcover.tif') as lulc:
    print (lulc.width, lulc.height)
    band = lulc.read()  # equivalent to gdal.Dataset.ReadAsArray()
    print 'Array shape', band.shape

    max_value = 0.
    for band_no, block_indices in lulc.block_windows():
        max_value = max(max_value, lulc.read(window=block_indices).max())
    print 'Max value', max_value

# Unsure how to only read in a single band.
print rasterio.open('/data/landcover.tif').read(window=(0, (0, 0),
                                                        (lulc.width, lulc.height)))


