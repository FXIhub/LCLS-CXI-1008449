#source files on cxi-monitor
source /cds/sw/ds/ana/conda1/manage/bin/psconda.sh
source /cds/home/opr/cxiopr/OM-GUI/cxi100844924/install/bin/activate-om

#copy the template sym link to the monitor file that om reads
cp template.yaml monitor.yaml


#file that actually runs om
mw=monitor_wrapper.sh


#write the file to run om
echo '#!/bin/bash' > $(pwd)/${mw}
echo '# File automatically created by the'  >> $(pwd)/${mw}
echo '# run_om.sh script' >> $(pwd)/${mw}
#source the envs
echo 'source /cds/sw/ds/ana/conda1/manage/bin/psconda.sh' >> $(pwd)/${mw}
echo 'source /cds/home/opr/cxiopr/OM-GUI/cxi100844924/install/bin/activate-om' >> $(pwd)/${mw}
#run om with online data source
echo "om_monitor.py 'shmem=psana.0:stop=no'" >> $(pwd)/${mw}
#make the file executeable
chmod +x $(pwd)/${mw}
#run the executable we wrote
$(which mpirun) --mca oob_tcp_if_exclude enp65s0f1,enp66s0 --oversubscribe --map-by ppr:2:node \
                --host daq-cxi-mon10,daq-cxi-mon11,daq-cxi-mon13,daq-cxi-mon14 $(pwd)/${mw}

