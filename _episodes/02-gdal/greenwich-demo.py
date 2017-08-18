import greenwich

with greenwich.Raster('/data/landcover.tif') as lulc:
    print 'LULC shape:', lulc.shape  # tuple of (row, col)
    raster_contents = lulc.array()
    masked_with_nodata = lulc.masked_array()

    print 'Nodata:', lulc.nodata


# Segfault, as expected
greenwich.Raster('/data/landcover.tif').GetRasterBand(1).GetNoDataValue()
