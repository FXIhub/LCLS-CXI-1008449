# LCLS-CXI-1008449
- Experiment Directory: `/sdf/data/lcls/ds/cxi/cxi100844924`
- SLACK chat: https://app.slack.com/client/E7SAV7LAD/C092393PP2B
- elog: https://pswww.slac.stanford.edu/lgbk/lgbk/cxi100844924/eLog

### SSH access
```
ssh amorgan@s3dflogin.slac.stanford.edu
ssh psana
cd /sdf/data/lcls/ds/cxi/cxi100844924
```

### Sourcing environment
Sources two envs, om must be installed for the second environment.
```
source ./source_this
```

### Installing om

Make a directory to save the om, and copy the current working version.
```
    mkdir ~/software
    cp -r /sdf/home/p/padams/software/om ~/software
```

Move to the directory you created and run the install script.
```
    cd ~/software/om
    ./tools/scripts/installation/instal.sh -p ~/software/install
```
    
### Running om (backend)
Make sure that variables are correctly set in the script.
```
cd om_scripts
./run_om [run]
```

### Running om (gui)
Ensure that the backend is running, and that tcp ip address is correctly set.
```
cd om_scripts
./run_gui
```

### Geometry conversion
Requires sourced environment.
```
geometry_convert -f 0-end.data -o [out file name]
```

### Generating masks
```
cd mask
python psana_mask.py -s exp=cxi100844924:run=16 -d jungfrau4M -o [out file name]
```

