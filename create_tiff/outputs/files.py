"""
Functions for writing output data into files.
"""

import sys
import os
import glob
import logging
import numpy as np
from netCDF4 import Dataset
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from osgeo import gdal, gdalconst
from osgeo import ogr, osr

from utils.tools import run_command

logger=logging.getLogger(__name__)
logging.basicConfig(format='%(message)s', level=logging.INFO)


def stats_nc_output(lonx, latx, wspdmean, wspdstd, wdirmean, wdirstd, outfile):
    """
    Write wind speed and direction mean an standard deviation into a netcdf file.
    
    Parameters
    ----------
    lon : 2D array of floats
        Longitude (degrees East).
    lat : 2D array of floats
        Latitude (degrees North).
    wspdmean : 2D array of floats
        Wind speed mean (m/s).
    wspdstd : 2D array of floats
        Wind speed standard deviation (m/s).
    wdirmean : 2D array of floats
        Wind direction mean (degrees from North).
    wdirstd : 2D array of floats
        Wind direction standard deviation (degrees from North).
    outfile : string
        Path to output file (netcdf).
    """
    logger.info('Output file: %s', outfile)
    # If exists, remove it
    if os.path.exists(outfile):
        os.remove(outfile)
    nx = wspdmean.shape[1]
    ny = wspdmean.shape[0]
    
    logger.info('Writing to the netcdf file.')
    outfile1 = Dataset(outfile, mode='w')
    # Global attributes
    outfile1.Conventions="CF-1.2"
    # Dimensions
    lon = outfile1.createDimension('lon',nx)
    lat = outfile1.createDimension('lat',ny)
    # Lat and lon
    lats = outfile1.createVariable('lat', np.float32, ('lat','lon'))
    lons = outfile1.createVariable('lon', np.float32, ('lat','lon'))
    lons.axis = 'X'
    lons.units = 'degree_east'
    lons.longname = 'Longitude'
    lons.coordinate_defines = 'point'
    lats.axis = 'Y'
    lats.units = 'degree_north'
    lats.longname = 'Latitude'
    lats.coordinate_defines = 'point'
    # Variable fields
    # Wind speed mean and std
    wspdm = outfile1.createVariable('wspdmean', np.float32, ('lat','lon'))
    wspdm.units = 'm/s'
    wspdm.longname = 'Mean Wind Speed'
    wspdm.grid_mapping = 'Lambert_Conformal'
    wspdm.coordinates = 'lat lon'
    wspds = outfile1.createVariable('wspdstd', np.float32, ('lat','lon'))
    wspds.units = 'm/s'
    wspds.longname = 'Wind Speed Standard Deviation'
    wspds.grid_mapping = 'Lambert_Conformal'
    wspds.coordinates = 'lat lon'
    # Wind direction mean and std
    wdirm = outfile1.createVariable('wdirmean', np.float32, ('lat','lon'))
    wdirm.units = 'degrees'
    wdirm.longname = 'Mean Wind Direction'
    wdirm.grid_mapping = 'Lambert_Conformal'
    wdirm.coordinates = 'lat lon'
    wdirs = outfile1.createVariable('wdirstd', np.float32, ('lat','lon'))
    wdirs.units = 'degrees'
    wdirs.longname = 'Wind Direction Standard Deviation'
    wdirs.grid_mapping = 'Lambert_Conformal'
    wdirs.coordinates = 'lat lon'
    # Writing data
    lats[:,:] = latx
    lons[:,:] = lonx
    wspdm[:,:] = wspdmean
    wspds[:,:] = wspdstd
    wdirm[:,:] = wdirmean
    wdirs[:,:] = wdirstd
    outfile1.close()
    return;


def tiff_output(lon, lat, dx, xvar, outfile):
    """
    Write specified variable as raster to tiff file.
    Coordinate reference system (CRS) is WGS 84, EPSG: 4326.
    
    Parameters
    ----------
    lon : 2D array of floats
        Longitude (degrees East).
    lat : 2D array of floats
        Latitude (degrees North).
    dx : float
        Pixel size. Usually same as grid cell size.
    xvar : 2D array of floats
        Variable to be written to tiff file.
    outfile : string
        Path to output file (GeoTiff).
    """
    logger.info('Output file: %s', outfile)
    # If exists, remove it
    if os.path.exists(outfile):
        os.remove(outfile)
    # Number of pixels in x and y direction, pixel size, projection
    nx = xvar.shape[1]
    ny = xvar.shape[0]
    xmin = np.min(lon[0,:])
    ymin = np.min(lat[:,0])
    logger.info('xmin, ymin: %f %f', xmin, ymin)
    WKTProj='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    logger.info('Writing to tiff file')
    driver = gdal.GetDriverByName('GTiff')
    data = driver.Create(outfile, nx, ny, 1, gdal.GDT_Float32,)
    # Geolocation (sets lat and lon for each array value)
    data.SetGeoTransform((xmin, dx, 0, ymin, 0, dx))
    data.SetProjection(WKTProj)
    data.GetRasterBand(1).WriteArray(xvar)
    data.GetRasterBand(1).SetNoDataValue(-9999)
    data.FlushCache()
    data = None
    return;


def nc_to_tiff(varnames, ncfile, outfile):
    """
    Convert netcdf file into a GeoTiff.
    Using GCP system, by utilizing gdal_translate command and 
    coordinates from 4 corners of netcdf file.
    
    Parameters
    ----------
    varnames : list of string
        Names of longitude, latitude and variable (within netcdf file) that will be translated into tiff.
    ncfile : string
        Path to input file (netcdf).
    outfile : string
        Path to output file (GeoTiff).
    """
    # Read coordinates from netcdf file
    f1 = Dataset(ncfile, mode='r')
    lon = f1.variables[varnames[0]][:,:]
    lat = f1.variables[varnames[1]][:,:]
    f1.close()
    x = [float(lon[-1,0]), float(lon[-1,-1]), float(lon[0,0]), float(lon[0,-1])]
    y = [float(lat[-1,0]), float(lat[-1,-1]), float(lat[0,0]), float(lat[0,-1])]
    nx = len(lon[0,:])-1
    ny = len(lon[:,0])-1
    logger.info('Mapping of 4 corners:')
    logger.info('(0, 0) -> lon[-1,0], lat[-1,0]')
    logger.info('(XSize,0) -> lon[-1,-1], lat[-1,-1]')  
    logger.info('(0,YSize) -> lon[0,0], lat[0,0]')
    logger.info('(XSize, YSize) -> lon[0,-1], lat[0,-1]')
    logger.info('Runing gdal_translate.')
    outfile1 = './tmp.tiff'
    # Taken out from gdal command (error otherwise): -a_srs EPSG:%i 4326
    command='gdal_translate -a_nodata %f -a_srs %s -gcp %i %i %f %f %f -gcp %i %i %f %f %f -gcp %i %i %f %f %f -gcp %i %i %f %f %f -of GTiff NETCDF:%s:%s %s' % (0.0, 'EPSG:4326', 0, 0, x[0], y[0], 0.00, nx, 0, x[1], y[1], 0.00, 0, ny, x[2], y[2], 0.0, nx, ny, x[3], y[3], 0.0, ncfile, varnames[2], outfile1)
    run_command(command)
    command1='gdalwarp -r near -order 1 -co COMPRESS=NONE -t_srs %s -dstalpha %s %s', ('EPSG:4326', outfile1, outfile)
    run_command(command1)
    if os.path.exists(outfile1):
        os.remove(outfile1)
    return;


class Shapefiles(object):

    """
    Functions that create different shapefiles.

    Outputs
    -------
    Shapefile outlining the tile coverage.
    Shapefile with wind components (u,v) and positions of each (u, v) pair.
    
    Parameters
    ----------
    suffix : string
        String that will be added at the end of all outfile names, before .shp
    """

    def __init__(self, suffix):
        self.suffix = suffix

    def tile_shapefile(self, lon, lat, outdir):
        """
        Create a shapefile with polygon around a tile or grid.

        Parameters
        ----------
        lon : 2D array of floats
            Longitude (degrees East).
        lat : 2D array of floats
            Latitude (degrees North).
        outdir : string
            Path to output file directory.
        """
        fname = 'tile_shape_' + self.suffix + '.shp'
        outfile = os.path.join(outdir, fname)
        logger.info('Output file: %s', outfile)
        # If exists, remove it
        if os.path.exists(outfile):
            os.remove(outfile)
        logger.info('Create a polygon around the area.')
        ring = None
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(float(lon[0,0]), float(lat[0,0]))
        ring.AddPoint(float(lon[-1,0]), float(lat[-1,0]))
        ring.AddPoint(float(lon[-1,-1]), float(lat[-1,-1]))
        ring.AddPoint(float(lon[0,-1]), float(lat[0,-1]))
        ring.AddPoint(float(lon[0,0]), float(lat[0,0]))
        sqr = ogr.Geometry(ogr.wkbPolygon)
        sqr.AddGeometry(ring)
        logger.info('Write a polygon into a shapefile.')
        driver = ogr.GetDriverByName('ESRI Shapefile')
        #Spatial reference
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        # Writing into shapefile
        dss = driver.CreateDataSource(outfile)
        layer = dss.CreateLayer('shape', srs, ogr.wkbPolygon)
        ft2 = ogr.Feature(layer.GetLayerDefn())
        ft2.SetGeometry(sqr)
        layer.CreateFeature(ft2)
        dss = layer = ft2 = None
        return;


    def wind_vectors_shapefile(self, lon, lat, u, v, outdir):
        """
        Create a shapefile with wind components.

        Parameters
        ----------
        lon : 2D array of floats
            Longitude (degrees East).
        lat : 2D array of floats
            Latitude (degrees North).
        u : 2D array of floats
            Zonal wind component (m/s).
        v : 2D array of floats
            Meridional wind component (m/s).
        outdir : string
            Path to output file directory.
        """
        fname = 'wind_components_' + self.suffix + '.shp'
        outfile = os.path.join(outdir, fname)
        logger.info('Output file: %s', outfile)
        # If exists, remove it
        if os.path.exists(outfile):
            os.remove(outfile)
        logger.info('Write wind components into a shapefile.')
        driver = ogr.GetDriverByName('ESRI Shapefile')
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        drv = driver.CreateDataSource(outfile)
        layer = drv.CreateLayer('wspd', srs, ogr.wkbPoint)
        layer.CreateField(ogr.FieldDefn('U', ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('V', ogr.OFTReal))
        n = 10  # skiping that many points
        for i in range(0,len(u[:,0]),n):
            for j in range(0,len(u[0,:]),n):
                ft = ogr.Feature(layer.GetLayerDefn())
                ft.SetField('U', float(u[i,j]))
                ft.SetField('V', float(v[i,j]))
                ft.SetGeometry(ogr.CreateGeometryFromWkt('POINT(%f %f)' % (lon[i,j],lat[i,j])))
                layer.CreateFeature(ft)
        drv = layer = ft = None
        return;
    
