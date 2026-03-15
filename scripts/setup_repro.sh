#!/bin/bash
# setup_repro.sh - Reproducible setup for Paper 007
# This script prepares the environment, extracts author code/data, and applies SLURM patches.

set -e

PAPER_DIR="repro-reviews/paper-007"
ZIP_SOURCE="../../AGILE_2026_CODE_DATA.zip" # Relative to paper root or absolute path
REPRO_DIR="$PAPER_DIR/repro"
DATA_DIR="$REPRO_DIR/data"
TMP_DIR="/tmp/paper-007-setup"

echo "Initializing Paper 007 Reproduction Setup..."

# 1. Ensure clean directory structure
mkdir -p "$REPRO_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$TMP_DIR"

# 2. Extract Author Package (Code and Data)
echo "Extracting author package..."
unzip -q "$ZIP_SOURCE" -d "$TMP_DIR"

# 3. Move Code to repro/
echo "Organizing code..."
cp -r "$TMP_DIR/AGILE_CODE_DATA/code/"* "$REPRO_DIR/"

# 4. Move Data to repro/data/ (Matching internal script expectations)
echo "Organizing data..."
cp -r "$TMP_DIR/AGILE_CODE_DATA/data/"* "$DATA_DIR/"

# 5. Apply SLURM Compatibility Patches
echo "Applying SLURM compatibility patches..."
# The original code used mp.cpu_count() - 8, which is unsafe on shared HPC nodes.
# We patch it to respect SLURM_CPUS_PER_TASK.
sed -i 's/num_chunks = mp.cpu_count() - 8/num_chunks = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))/' "$REPRO_DIR/routing_filters_nofilters.py"
sed -i 's/num_chunks = mp.cpu_count() - 8/num_chunks = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))/' "$REPRO_DIR/routing_filter_variations.py"

# 6. Cleanup
rm -rf "$TMP_DIR"

echo "Setup Complete. Track path: $PAPER_DIR"
