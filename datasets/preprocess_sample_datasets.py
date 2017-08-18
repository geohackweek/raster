import os
import tempfile
import logging

from osgeo import gdal, ogr
import pygeoprocessing

logging.basicConfig()

WGS84UTM11N = """PROJCS["WGS 84 / UTM zone 11N",
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
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-117],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32611"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]"""


def reproject_raster_to_epsg3718(in_filename, out_filename, cell_size):
    print 'Reprojecting %s -> %s' % (in_filename, out_filename)
    pygeoprocessing.reproject_dataset_uri(
        original_dataset_uri=in_filename,
        pixel_spacing=cell_size,
        output_wkt=WGS84UTM11N,
        resampling_method='nearest',
        output_uri=out_filename)

def convert_vector_extents_to_vector(in_vector, out_vector_uri):
    """Build a vector with 1 polygon that represents the raster's bounding box.

        raster_uri - a URI to a GDAL raster from which our output vector should
            be created
        sample_vector_uri - a URI to an OGR datasource that we will write on
            disk.  This output vector will be an ESRI Shapefile format.

        Returns Nothing."""

    _vector = ogr.Open(in_vector)
    _layer = _vector.GetLayer()
    layer_srs = _layer.GetSpatialRef()
    extent = _layer.GetExtent()

    driver = ogr.GetDriverByName('ESRI Shapefile')
    out_vector = driver.CreateDataSource(out_vector_uri)
    layer_name = str(os.path.basename(os.path.splitext(out_vector_uri)[0]))
    out_layer = out_vector.CreateLayer(layer_name, srs=layer_srs)

    poly_ring = ogr.Geometry(type=ogr.wkbLinearRing)

    # make a polygon for the bounding box
    poly_ring.AddPoint(extent[0], extent[2]),
    poly_ring.AddPoint(extent[1], extent[2]),
    poly_ring.AddPoint(extent[1], extent[3]),
    poly_ring.AddPoint(extent[0], extent[3]),
    poly_ring.AddPoint(extent[0], extent[2]),
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(poly_ring)

    feature = ogr.Feature(out_layer.GetLayerDefn())
    feature.SetGeometry(polygon)
    out_layer.CreateFeature(feature)
    out_vector.SyncToDisk()

    ogr.DataSource.__swig_destroy__(out_vector)
    feature = None
    out_layer = None
    out_vector = None


def prepare_landcover(lulc_path, clip_to_vector, out_lulc_path):
    # LULC doesn't have a nodata value set, which causes problems.
    ds = gdal.Open(lulc_path, gdal.GA_Update)
    band = ds.GetRasterBand(1)
    band.SetNoDataValue(255.0)
    band.FlushCache()
    band = None
    ds.FlushCache()
    ds = None

    # Create a sample raster to clip to based on the vector extents provided.
    tempdir = tempfile.mkdtemp(dir=os.getcwd())

    print 'New vector from bounding box of %s' % clip_to_vector
    boundingbox_vector = os.path.join(tempdir, 'sierra_bbox.shp')
    convert_vector_extents_to_vector(clip_to_vector, boundingbox_vector)

    lulc_srs = pygeoprocessing.get_dataset_projection_wkt_uri(lulc_path)

    # reproject the vector to the target projection
    print 'Reprojecting %s to LULC SRS' % boundingbox_vector
    projected_vector = os.path.join(tempdir, 'sierra_bbox_projected.shp')
    pygeoprocessing.reproject_datasource_uri(boundingbox_vector, lulc_srs,
                                             projected_vector)

    clipped_lulc = os.path.join(tempdir, 'lulc_clipped.tif')
    print 'Clipping the LULC %s by %s -> %s' % (lulc_path,
                                                projected_vector,
                                                clipped_lulc)
    pygeoprocessing.clip_dataset_uri(
        lulc_path, projected_vector, clipped_lulc,
        assert_projections=False)  # Datasets are unprojected, so don't check

    reproject_raster_to_epsg3718(
        clipped_lulc, out_lulc_path, 500.0)  # 500m pixel size


if __name__ == '__main__':
    output_dir = 'reprojected'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # reproject yosemite vector
    # Yosemite vector is an excerpt from the National Park Service.
    # Full citation:
    # 2016. Administrative Boundaries of National Park System
    # Units 9/30/2016 - National Geospatial Data Asset (NGDA) NPS National
    # Parks Dataset. NPS - Land Resources Division
    pygeoprocessing.reproject_datasource_uri('yosemite.shp', WGS84UTM11N,
                                             os.path.join(output_dir, 'yosemite.shp'))

    # reproject DEMs
    # DEMs are stored in this folder, and unzipped in-place.
    # ASTER GDEM is a product of METI and NASA.
    for aster_name in ['ASTGTM2_N38W120', 'ASTGTM2_N37W120']:
        raster_filename = os.path.join(aster_name, '%s_dem.tif' % aster_name)
        ds = gdal.Open(raster_filename, gdal.GA_Update)
        band = ds.GetRasterBand(1)
        band.SetNoDataValue(-1)
        band.FlushCache()
        band = None
        ds = None

        out_raster = os.path.join(output_dir,
                                  '%s.tif' % aster_name.split('_')[1])
        reproject_raster_to_epsg3718(raster_filename, out_raster, 30)

    # This is a vector of the south sierra region of california.
    # Retrieved from http://www.fs.usda.gov/detail/r5/landmanagement/resourcemanagement/?cid=stelprdb5347192
    south_sierra_vector = 'ExistingVegSouthSierra2000_2008_v1.gdb'

    # prepare LULC
    # LULC is based on MODIS data, and can be downloaded from
    # http://landcover.usgs.gov/global_climatology.php
    # Full citation:
    # Broxton, P.D., Zeng, X., Sulla-Menashe, D., Troch, P.A., 2014a: A
    # Global Land Cover Climatology Using MODIS Data. J. Appl. Meteor.
    # Climatol., 53, 1593 1605. doi:http://dx.doi.org/10.1175/JAMC-D-13-0270.1
    prepare_landcover('LCType.tif', south_sierra_vector,
                      os.path.join(output_dir, 'landcover.tif'))
