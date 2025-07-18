#!/bin/bash
# File automatically created by the
# run_om.sh script
source /cds/sw/ds/ana/conda1/manage/bin/psconda.sh
source /cds/home/opr/cxiopr/OM-GUI/cxi100844924/install/bin/activate-om
om_monitor.py 'shmem=psana.0:stop=no'
