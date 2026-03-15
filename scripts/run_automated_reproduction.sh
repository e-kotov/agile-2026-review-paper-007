#!/bin/bash
#SBATCH --job-name=paper007_automated
#SBATCH --output=repro-reviews/paper-007/logs/automated_%j.out
#SBATCH --error=repro-reviews/paper-007/logs/automated_%j.err
#SBATCH --partition=scc-cpu
#SBATCH --account=scc_mrdf_all
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=96G
#SBATCH --time=06:00:00

set -e
module load apptainer

WORKSPACE="/mnt/ceph-ssd/workspaces/ws/scc_mrdf_all/u14190-agile-2026"
PAPER_DIR="$WORKSPACE/repro-reviews/paper-007"
CONTAINER="$PAPER_DIR/container.sif"

echo "================================================================================"
echo "Starting Automated Full Reproduction of Paper 007 at $(date)"
echo "Resources Allocated: $SLURM_CPUS_PER_TASK Cores, 96GB RAM"
echo "================================================================================"

# ------------------------------------------------------------------------------
# 1. Environment Setup & Isolation
# ------------------------------------------------------------------------------
echo "[1/4] Setting up isolated automated environment..."
rm -rf "$PAPER_DIR/repro_automated" "$PAPER_DIR/results_automated" "$PAPER_DIR/plots_automated"
mkdir -p "$PAPER_DIR/results_automated/vienna"
mkdir -p "$PAPER_DIR/plots_automated"
mkdir -p "$PAPER_DIR/logs"

# Copy original code to an isolated directory so we don't mess up the author's exact files
cp -r "$PAPER_DIR/repro" "$PAPER_DIR/repro_automated"

# ------------------------------------------------------------------------------
# 2. Dynamic Code Patching
# ------------------------------------------------------------------------------
echo "[2/4] Applying robust computational patches..."

# Patch 1: Reroute outputs to results_automated and plots_automated
find "$PAPER_DIR/repro_automated" -type f -name "*.py" -exec sed -i "s/'results'/'results_automated'/g" {} +
find "$PAPER_DIR/repro_automated" -type f -name "*.py" -exec sed -i "s/'plots'/'plots_automated'/g" {} +

# Patch 2: Fix hardcoded CPU allocation (Thread thrashing)
find "$PAPER_DIR/repro_automated" -type f -name "*.py" -exec sed -i 's/mp\.cpu_count() - 8/int(os.environ.get("SLURM_CPUS_PER_TASK", 1))/g' {} +

# Patch 3: Fix zero-division error in chunking logic
find "$PAPER_DIR/repro_automated" -type f -name "*.py" -exec sed -i 's/n = int(len(ods) \/ num_chunks)/n = max(1, int(len(ods) \/ num_chunks))/g' {} +

# ------------------------------------------------------------------------------
# 3. Pipeline Execution
# ------------------------------------------------------------------------------
echo "[3/4] Beginning computational pipeline..."

# We MUST cd into the code directory because the authors used os.getcwd() for path resolution
cd "$PAPER_DIR/repro_automated"

run_step() {
    local script_name=$1
    echo "--------------------------------------------------------------------------------"
    echo "Executing: $script_name"
    echo "Started at $(date)"
    # Run inside container, binding the workspace to handle absolute path resolutions
    apptainer exec --bind "$WORKSPACE":"$WORKSPACE" "$CONTAINER" python -u "$script_name" 2>&1
    echo "Finished at $(date)"
}

# Step A: Compute the Fastest Path and Inclusive baselines (nofilters, filters)
run_step "routing_filters_nofilters.py"

# Step B: Compute all 12 parametric threshold variations (transitions)
run_step "routing_filter_variations.py"

# Step C: Group the output CSVs by route_nr
run_step "route_nr_group.py"

# Step D: Generate Final Tables and Figures
echo "[4/4] Generating Final Figures..."
run_step "no_filters.py"
run_step "filter_variations.py"

echo "================================================================================"
echo "AUTOMATED REPRODUCTION COMPLETED SUCCESSFULLY at $(date)"
echo "Output Data: $PAPER_DIR/results_automated/"
echo "Output Plots: $PAPER_DIR/plots_automated/"
echo "================================================================================"
