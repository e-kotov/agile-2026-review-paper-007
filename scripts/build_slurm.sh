#!/bin/bash
#SBATCH --job-name=build_paper007
#SBATCH --output=repro-reviews/paper-007/logs/build_%j.out
#SBATCH --error=repro-reviews/paper-007/logs/build_%j.err
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00

module load apptainer
cd repro-reviews/paper-007
apptainer build --fakeroot container.sif apptainer.def
