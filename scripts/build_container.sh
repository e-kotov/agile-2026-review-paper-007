#!/bin/bash
#SBATCH --job-name=build_paper007_container
#SBATCH --output=build_paper007_%j.log
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00

module load apptainer

# Assume run from paper root
apptainer build container.sif apptainer.def
