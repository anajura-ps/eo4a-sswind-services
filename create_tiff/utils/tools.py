"""
General tools
"""

import logging
import shlex
import subprocess
import datetime as dt
import numpy as np

logger=logging.getLogger(__name__)
logging.basicConfig(format='%(message)s', level=logging.INFO)


def longitude_fix(lon):
    """
    Change the longitude range from 0 to 360 into -180 to 180.

    Parameters
    -----------
    lon : array of floats
        Longitude (degrees) array that needs to be changed.
    """
    indl = np.where((lon>180))
    lon[indl] = lon[indl]-360
    return;


def land_mask(wspd):
    """
    Mask the land. Land is determined by zero wind speed.

    Parameters
    -----------
    wspd : array of floats
        Wind speed array (m/s).

    Returns
    -------
    m : array of floats
        Land mask (1 over sea, NaN over land).
    """
    m = np.ones(wspd.shape)
    ind = np.where(wspd < 0.001)
    m[ind] = np.nan
    return m;


def wind_components(wspd, wdir):
    """
    Calculate the wind components (u,v) from wind speed and direction.
    
    Parameters
    ----------
    wspd : array of floats
        Wind speed (m/s).
    wdir : array of floats
        Wind direction (degrees).
    
    Returns
    -------
    u : array of floats
        Zonal wind speed component (m/s).
    v : array of floats
        Meridional wind speed component (m/s).
    """
    cosdir = np.cos(wdir*np.pi/180)
    sindir = np.sin(wdir*np.pi/180)
    u = wspd*sindir*(-1)
    v = wspd*cosdir*(-1)
    return u, v;


def wind_direction_from_uv(u, v):
    """
    Calculate wind direction from zonal and meridional wind components.
    
    Notes
    -----
    This is for arrays, calculation for single (u,v) pair should be done separately
    
    Parameters
    ----------
    u : array of floats
        Zonal wind component.
    v : array of floats
        Meridional wind component.
    
    Returns
    -------
    wdir : array of floats
        Wind direction.
    """
    # Conversion factor, from radians to degrees
    rtod = 180/np.pi
    # Calculating meteorological wind direction
    # (direction from where wind is coming from, with respect to true north)
    wdir = 270-(np.arctan2(v,u)*rtod)
    # If there is an angle larger than 360 (usually NE quadrant),
    # express it in [0-90]
    ind360 = np.where(wdir >= 360)
    wdir[ind360] = wdir[ind360] - 360
    return wdir;


def wind_direction_std(wdir):
    """
    Calculate wind direction standard deviation, by using the Yamartino method.
    Yamartino method is the most common calculation of standard deviation 
    for wind speed, considering its angular nature.
    This method is described in Yamartino (1984).
    
    Parameters
    ----------
    wdir : array of floats
        Wind direction.
    
    Returns
    -------
    wdirstd : array of floats
        Wind direction standard deviation, calculated by Yamartino method.
    """
    # Conversion factor, degrees to radians
    dtor = np.pi/180
    # Convert wind direction from degrees to radians,
    # because the numpy angular functions expect radians
    wdirr = wdir*dtor
    # Averge values of sin and cos
    sa = np.nanmean(np.sin(wdirr), axis=-1)
    ca = np.nanmean(np.cos(wdirr), axis=-1)
    # Parameter epsilon (always between 0 and 1)
    eps = np.sqrt(1-np.power(sa,2)-np.power(ca,2))
    # Standard deviation function found by Yamartino
    wdirstd = np.arcsin(eps)*(1+0.1547*np.power(eps,3))
    return wdirstd;
    
    

def time_seconds_to_datetime64(t, year, month, day):
    """
    Converts time from seconds-since-{year}-{month}-{day}T00:00:00Z to date and time.

    Parameters
    -----------
    t : array of floats
        Time from input file (seconds since the reference date)
    year : int
        Year of the reference date
    month : int
        Month of the reference date
    day : int
        Day of the reference date
    
    Returns
    -------
    dates : array of datetime64
        Time from input file, in numpy datetime64[s] format (YYYY-MM-DDTHH:MM:SS)
    """
    date0 = dt.datetime(year,month,day)
    days1 = t/(24.0*3600.0)
    # dates type - format: datetime64[s] - YYYY-MM-DDTHH:MM:SS 
    dates = np.empty(days1.shape, dtype='datetime64[s]')
    for i in range(days1.shape[0]):
        dates[i] = np.datetime64(date0+dt.timedelta(days=days1[i]))
    return dates;


def time_datetime64_to_string(dates0):
    """
    Converts time from numpy datetime64[s] to YYYYMMDDTHHMMSS.

    Parameters
    -----------
    dates0 : array of datetime64
        Date and time in numpy datetime64[s] format.

    Returns
    -------
    dates : list of strings
        Date and time in format YYYYMMDDTHHMMSS.
    """
    dates = np.empty(dates0.shape, dtype='object')
    for i in range(dates0.shape[0]):
        d1 = str(dates0[i]).split('-')[:]
        d2 = d1[-1].split(':')[:]
        dates[i] = d1[0]+d1[1]+d2[0]+d2[1]+d2[2]
    return dates;



def collect_region_wspdwdir(lon, lat, wspd, wdir, coords):
    """
    Collect wind speed and direction data within a region of interest (ROI).
    
    Parameters
    ----------
    lon : array of floats
        Longitude (degrees East).
    lat : array of floats
        Latitude (degrees North).
    wspd : array of floats
        Wind speed (m/s) from the input file.
    wdir : array of floats
        Wind direction (degrees) from the input file.
    coords : array of floats, length 4
        Coordinates for the region bounding box, [lon1, lon2, lat1, lat2].
    
    Returns
    -------
    wspdh : array of floats
        Wind speed (m/s) values collected within the region of interest.
    wdirh : array of floats
        Wind direction (degrees) values collected within the region of interest.
    """
    wspdh = []
    wdirh = []
    ind = np.where((lon>=coords[0]) & (lon<=coords[1]) & (lat>=coords[2]) & (lat<=coords[3]))
    wspdh = np.append(wspdh, wspd[ind])
    wdirh = np.append(wdirh, wdir[ind])
    return wspdh, wdirh;


def collect_region_wspd(lon, lat, wspd, coords):
    """
    Collect wind speed data (no direction) within a region of interest (ROI).
    
    Parameters
    ----------
    lon : array of floats
        Longitude (degrees East).
    lat : array of floats
        Latitude (degrees North).
    wspd : array of floats
        Wind speed (m/s) from the input file.
    coords : array of floats, length 4
        Coordinates for the region bounding box, [lon1, lon2, lat1, lat2].
    
    Returns
    -------
    wspdh : array of floats
        Wind speed (m/s) values collected within the region of interest.
    """
    wspdh = []
    ind = np.where((lon>=coords[0]) & (lon<=coords[1]) & (lat>=coords[2]) & (lat<=coords[3]))
    wspdh = np.append(wspdh, wspd[ind])
    return wspdh;


def buoy_within(lon, lat, coords):
    """
    Establish buoy's position and check if it is within region of interest.
    
    EMODnet buoys contain the array of coordinates, with length same as time.
    However, buoys is at the same position, so all values are the same.
    This function returns a boolean which is True if the buoy is within ROI.
    
    Parameters
    ----------
    lon : array of floats
        Buoy's longitude (degrees East)
    lat : array of floats
        Buoy's latitude (degrees North)
    coords: array of floats, length 4
        Coordinates for the region bounding box, [lon1, lon2, lat1, lat2].
    
    Returns
    -------
    binroi : bool
        True if buoy is within ROI, false otherwise. 
    """
    lonb = np.nanmean(lon, axis=0)
    latb = np.nanmean(lat, axis=0)
    if (lonb >= coords[0]) and (lonb <= coords[1]) and (latb >= coords[2]) and (lonb <= coords[3]):
        binroi = True
    else:
        binroi = False
    return binroi;



def run_command(command):
    """
    Run command-line tools, e.g. gdal utilities. 
    Stdout and stderr are logged.
    
    Parameters
    ----------
    command : string
        Command and parameters.
    """
    logger.info('Command: %s' % command)
    process = subprocess.Popen(shlex.split(command), bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    fp = process.stdout
    while True:
        line = fp.readline()
        if not line:
            break
        logger.info(line.strip())
