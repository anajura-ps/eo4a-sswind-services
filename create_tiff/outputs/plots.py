"""
Functions for creating plots and saving them as images.
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

logger=logging.getLogger(__name__)
logging.basicConfig(format='%(message)s', level=logging.INFO)


class CreatePlot(object):
    """
    Create an image, depending on chosen function.
    
    Choices are: histogram, dailymean, two contourplots.
    """

    def plot_histogram(self, wspdh, wdirh, outfile):
        """
        Create an image of wind speed and direction histograms.

        Parameters
        ----------
        wspdh : 1D array of floats
            Wind speed values from specified region and time range.
        wdirh : 1d arrray of floats
            Wind direction values from specified region and time range.
        outfile : string
            Path of the output file. 
        """
        logger.info('Output file: %s', outfile)
        # If exists, remove it
        if os.path.exists(outfile):
            os.remove(outfile)
        logger.info('Creating histogram image.')
        plt.figure()
        # Wind speed
        sp=plt.subplot(2,1,1)
        bs=[0,3.5,7,10.5,14,17.5,21,25]
        h1=plt.hist(wspdh, bins=bs, range=(0,25))
        plt.xticks(bs)
        plt.title('Wind speed (m/s)')
        # Wind direction
        sp=plt.subplot(2,1,2)
        bs=np.linspace(0,360,9)
        h1=plt.hist(wdirh, bins=bs, range=(0,360))
        plt.xticks(bs)
        plt.title('Wind direction ($^o$ from N)')
        vE=plt.axvline(x=90,color='k')
        vS=plt.axvline(x=180,color='k')
        vW=plt.axvline(x=270,color='k')
        ymin, ymax = plt.ylim()
        tNE=plt.text(10,0.9*ymax,'NE')
        tSE=plt.text(100,0.9*ymax,'SE')
        tSW=plt.text(190,0.9*ymax,'SW')
        tNW=plt.text(280,0.9*ymax,'NW')
        ax=plt.axis([0,360,ymin,ymax])
        plt.tight_layout()
        plt.savefig(outfile)


    def plot_timeseries(self, dates, skp, vardm, varlabel, outfile):
        """
        Create an image of a time series, for a specified variable (vardm). 
        For example, wind speed daily mean time series.

        Parameters
        ----------
        dates : array of datetime64
            Dates from time series, in datetime64 format.
        skp : int
           Number of dates elements to be skipped for ticks.
        vardm : array of floats
            Time series of a specified variable.
        varlabel : string
            Label for the variable.
        outfile : string
            Path of the output file.
        """
        logger.info('Output file: %s', outfile)
        # If exists, remove it
        if os.path.exists(outfile):
            os.remove(outfile)
        logger.info('Creating time series image.')
        plt.figure()
        plt.plot(vardm)
        plt.title('Time series')
        plt.ylabel(varlabel)
        datesstr=[str(dates[0]).split('T')[0]]
        for i in range(1,len(dates)):
            datesstr.append(str(dates[i]).split('T')[0])
        plt.xticks(np.arange(0,len(dates),skp), (datesstr[::skp]))
        plt.xlabel('Date')
        plt.savefig(outfile)


    def plot_two_contourplots(self, lon, lat, a, titlea, b, titleb, outfile):
        """
        Create an image of two contour plots, with any variable combination.
        For example, wind speed and direction means, or wind speed mean and standard deviation.

        Parameters
        ----------
        lon : array of floats
            Longitude values of grid points.
        lat : array of floats
            Latitude values of grid points.
        a : array of floats
            Array to be plotted on top subplot.
        titlea : string
            Title of top subplot.
        b : array of floats
            Array to be plotted on bottom subplot.
        titleb : string
            Title of bottom subplot.
        outfile : string
            Path to output file.
        """
        logger.info('Output file: %s', outfile)
        # If exists, remove it
        if os.path.exists(outfile):
            os.remove(outfile)
        plt.figure()
        plt.subplot(2,1,1)
        plt.contourf(lon, lat, a)
        plt.colorbar()
        plt.title(titlea)
        plt.ylabel('Latitude ($^o$N)')
        plt.subplot(2,1,2)
        plt.contourf(lon, lat, b)
        plt.colorbar()
        plt.title(titleb)
        plt.xlabel('Longitude ($^o$E)')
        plt.ylabel('Latitude ($^o$N)')
        plt.tight_layout()
        plt.savefig(outfile)
