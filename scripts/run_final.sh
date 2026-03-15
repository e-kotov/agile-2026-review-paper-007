#!/bin/bash
#SBATCH --job-name=paper007_final
#SBATCH --output=repro-reviews/paper-007/logs/final_%j.out
#SBATCH --error=repro-reviews/paper-007/logs/final_%j.err
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=128G
#SBATCH --time=24:00:00

set -e
module load apptainer

CONTAINER="/mnt/ceph-ssd/workspaces/ws/scc_mrdf_all/u14190-agile-2026/repro-reviews/paper-007/container.sif"
WORKSPACE="/mnt/ceph-ssd/workspaces/ws/scc_mrdf_all/u14190-agile-2026"
REPRO_DIR="$WORKSPACE/repro-reviews/paper-007/repro"

echo "Starting Final Paper 007 Reproduction at $(date)"
echo "Resources: 48 Cores, 192GB RAM"

run_step() {
    local script_name=$1
    echo "--------------------------------------------------------------------------------"
    echo "STEP: $script_name"
    echo "Started at $(date)"
    cd "$REPRO_DIR"
    apptainer exec --bind "$WORKSPACE":"$WORKSPACE" "$CONTAINER" python -u "$script_name" 2>&1
    echo "Finished at $(date)"
}

# Step 1: Complete the remaining routing variations (Skips what's already in results_final)
run_step "routing_filter_variations_final.py"

# Step 2: Grouping (Uses results_final)
run_step "route_nr_group_final.py"

# Step 3: Plotting (Uses results_final)
run_step "no_filters_final.py"
run_step "filter_variations_final.py"

echo "ALL STEPS COMPLETED SUCCESSFULLY at $(date)"
