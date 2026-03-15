#!/bin/bash
#SBATCH --job-name=paper007_analysis
#SBATCH --output=analysis_%j.log
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00

module load apptainer

# Path to the container
CONTAINER="./container.sif"

# Check if container exists
if [ ! -f "$CONTAINER" ]; then
    echo "Error: Container not found at $CONTAINER"
    exit 1
fi

# Run the analysis scripts inside the container
# Step 1: Routing Computation
apptainer exec "$CONTAINER" python repro/routing_filters_nofilters.py
apptainer exec "$CONTAINER" python repro/routing_filter_variations.py

# Step 2: Route Number Grouping
apptainer exec "$CONTAINER" python repro/route_nr_group.py

# Figures and Tables Reproduction
apptainer exec "$CONTAINER" python repro/no_filters.py
apptainer exec "$CONTAINER" python repro/filter_variations.py
