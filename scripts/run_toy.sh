#!/bin/bash
#SBATCH --job-name=paper007_toy
#SBATCH --output=repro-reviews/paper-007/logs/toy_%j.out
#SBATCH --error=repro-reviews/paper-007/logs/toy_%j.err
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00

set -e
module load apptainer

WORKSPACE="/mnt/ceph-ssd/workspaces/ws/scc_mrdf_all/u14190-agile-2026"
PAPER_DIR="$WORKSPACE/repro-reviews/paper-007"
CONTAINER="$PAPER_DIR/container.sif"

echo "Starting Toy Reproduction at $(date)"

run_step() {
    local script_name=$1
    echo "--------------------------------------------------------------------------------"
    echo "STEP: $script_name"
    cd "$PAPER_DIR/repro_toy"
    apptainer exec --bind "$WORKSPACE":"$WORKSPACE" "$CONTAINER" python -u "$script_name" 2>&1
}

# Run the full pipeline on the toy dataset
run_step "routing_filters_nofilters.py"
run_step "routing_filter_variations.py"
run_step "route_nr_group.py"
run_step "no_filters.py"
run_step "filter_variations.py"

echo "TOY REPRODUCTION COMPLETED SUCCESSFULLY at $(date)"
