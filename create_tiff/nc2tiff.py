"""
Convert netcdf to tiff.
"""

import os
import sys
import glob
import logging
import argparse

from outputs.files import nc_to_tiff

def main(argv):
 
    # Getting the command-line input with parser and running everything
    parser=argparse.ArgumentParser(description="Convert input netcdf file to GeoTiff")
    parser.add_argument('ncfile', type=str, help='input netcdf file')
    parser.add_argument('outdir', type=str, help='output tiff file directory')
    args = parser.parse_args()

    varnames = ['owiLon', 'owiLat', 'owiWindSpeed']
    outfile = os.path.join(args.outdir, 'TestTiff.tiff')
    nc_to_tiff(varnames, args.ncfile, outfile)
    

if __name__=="__main__":
    sys.exit(main(sys.argv))
