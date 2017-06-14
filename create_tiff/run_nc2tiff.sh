apt-get install -y unzip

export PYTHONPATH=".:PYTHONPATH"

zipfile=$1
outdir=$2

unzip -o $zipfile -d /data_service/
# Creating the netcdf file path
# Doing it manually now, to be quicker
#dir1=$( dirname pwd )
dir1='/data_service/'
suff='S1A_IW_OCN__2SDV_20170610T180620_20170610T180645_016975_01C425_5D02.SAFE/measurement/s1a-iw-ocn-vv-20170610t180027-20170610t180059-016975-01C425-001.nc'
ncfile=${dir1}${suff}

python nc2tiff.py $ncfile $outdir

