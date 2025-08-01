#!/bin/bash
#SBATCH --partition=milano
#SBATCH --account=lcls:cxi100844924
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --time=10:00:00
#SBATCH -J powder
#SBATCH -o powder.out
#SBATCH -e powder.out

source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh

mpirun -n 32 python powder.py $1
