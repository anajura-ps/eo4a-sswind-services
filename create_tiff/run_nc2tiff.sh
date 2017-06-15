set -e

apt-get update
apt-get install -y unzip

export PYTHONPATH=".:PYTHONPATH"

zipdir=$1
outdir=$2

for zipfile in $zipdir/*.zip
do
    unzip -o $zipfile -d /data_service/
done

# Creating the netcdf file path
# Doing it manually now, to be quicker
#dir1=$( dirname pwd )
dir1='/data_service/'
suff='S1A_IW_OCN__2SDV_*.SAFE/measurement/s1*.nc'
ncfile=${dir1}${suff}


for ncfile1 in $ncfile
do
    python nc2tiff.py $ncfile1 $outdir
done


