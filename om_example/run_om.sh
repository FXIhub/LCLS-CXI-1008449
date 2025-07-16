# In the last line, replace **X** with the number of OM nodes to run on each
# machine and **Y** with a comma-separated list of hostnames corresponding to the
# machines on which OnDA should run.

RUN=$1
RUN_STR=$(printf "%04d" $RUN)
maskfn=cxip18619_r4_mask.h5
geomfn=cspad_v2.geom
dir=hdf5/test_r$RUN_STR
expt='cxip18619'
QUEUE='milano'
CORES=4


if [[ ! -e $dir ]]; then
    mkdir -p $dir
elif [[ ! -d $dir ]]; then
    echo "$dir already exists but is not a directory" 1>&2
fi

cd $dir

cp ../../template-jungfrau.yaml monitor.yaml
cp ../../${geomfn} .
cp ../../${maskfn} .
#cp ../../${darkcalfn} .

sed -i "s/RUN/$RUN_STR/" monitor.yaml
sed -i "s/MASKFILE/$maskfn/" monitor.yaml
#sed -i "s/DARKCALFILE/$darkcalfn/" monitor.yaml
sed -i "s/GEOMFILE/$geomfn/" monitor.yaml

mw=monitor_wrapper.sh

DATASOURCE="exp=$expt:run=$RUN " ##new specfic datasource

source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh
source ~/software/install/bin/activate-om
echo Creating and Running $(pwd)/${mw}
echo '#!/bin/bash' > $(pwd)/${mw}
echo '# File automatically created by the'  >> $(pwd)/${mw}
echo '# run_om.sh script' >> $(pwd)/${mw}
echo 'source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh' >> $(pwd)/${mw}
echo 'source ~/software/install/bin/activate-om' >> $(pwd)/${mw}
echo "om_monitor.py ${DATASOURCE}" >> $(pwd)/${mw}
chmod +x $(pwd)/${mw}

mpirun -n ${CORES} $(pwd)/${mw}
