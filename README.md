# LCLS-CXI-1008449
- Experiment Directory: `/sdf/data/lcls/ds/cxi/cxi100844924`
- SLACK chat: https://app.slack.com/client/E7SAV7LAD/C092393PP2B
- elog: https://pswww.slac.stanford.edu/lgbk/lgbk/cxi100844924/eLog

### SSH access
```
# optional
ssh-keygen 
ssh-copy-id amorgan@s3dflogin.slac.stanford.edu

ssh -Y amorgan@s3dflogin.slac.stanford.edu

# optional
ssh-keygen 
ssh-copy-id psana

ssh psana
cd /sdf/data/lcls/ds/cxi/cxi100844924
```

### Github push permissions
Point ssh to deployed key for automatic push permissions:
```
echo "Host LCLS-CXI-1008449 github.com
Hostname github.com
IdentityFile /sdf/scratch/lcls/ds/cxi/cxi100844924/scratch/LCLS-CXI-1008449/ssh/github_rsa" >> ~/.ssh/config
```
this is not needed if you want to edit then push using your own github account + keys.

### Sourcing environment
Sources two envs, om must be installed for the second environment.
```
cd scratch/LCLS-CXI-1008449
source ./source_this
```

### Look at frames
after ssh'ing (as above with -Y argument)
```
python analysis/look_at_frames.py <run_number>
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

### Editing masks
Requires source environment.
```
cheetah_view.py [hdf5 file]
```

