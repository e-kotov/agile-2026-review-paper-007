#!/bin/bash
#SBATCH --job-name=paper007_verbose
#SBATCH --output=repro-reviews/paper-007/logs/analysis_%j.out
#SBATCH --error=repro-reviews/paper-007/logs/analysis_%j.err
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=06:00:00

set -e
module load apptainer

# Create logs directory if it doesn't exist
mkdir -p repro-reviews/paper-007/logs

# Path to the container
CONTAINER="/mnt/ceph-ssd/workspaces/ws/scc_mrdf_all/u14190-agile-2026/repro-reviews/paper-007/container.sif"

# Check if container exists
if [ ! -f "$CONTAINER" ]; then
    echo "Error: Container not found at $CONTAINER"
    exit 1
fi

echo "Starting Paper 007 Verbose Analysis at $(date)"
echo "SLURM_CPUS_PER_TASK: $SLURM_CPUS_PER_TASK"

# Helper to run scripts with timing and logging
run_step() {
    local script_name=$1
    echo "--------------------------------------------------------------------------------"
    echo "STEP: $script_name"
    echo "Started at $(date)"
    
    # Change to the repro directory so relative paths in authors' scripts work
    cd /mnt/ceph-ssd/workspaces/ws/scc_mrdf_all/u14190-agile-2026/repro-reviews/paper-007/repro
    
    # Run inside container, capturing all output
    if apptainer exec --bind /mnt/ceph-ssd/workspaces/ws/scc_mrdf_all:/mnt/ceph-ssd/workspaces/ws/scc_mrdf_all "$CONTAINER" python -u "$script_name" 2>&1; then
        echo "SUCCESS: $script_name"
    else
        echo "FAILURE: $script_name"
        echo "Check the .err file and the end of this .out file for tracebacks."
        exit 1
    fi
    cd - > /dev/null
    echo "Finished at $(date)"
}

# Step 1: Routing Computation (Baseline)
run_step "routing_filters_nofilters.py"

# Step 1b: Routing Computation (Variations)
run_step "routing_filter_variations.py"

# Step 2: Route Number Grouping
run_step "route_nr_group.py"

# Step 3: Figures and Tables Reproduction
run_step "no_filters.py"
run_step "filter_variations.py"

echo "Finished Paper 007 Verbose Analysis at $(date)"
