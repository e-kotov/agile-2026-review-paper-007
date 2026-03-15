# Reproduction of Paper 007: Inclusive Multimodal Routing: Who Gets Left Behind?

This repository contains the reproduction artifacts for AGILE 2026 Paper 007.

## Structure

- `repro/`: Original author code.
- `report/`: Quarto report documenting the reproduction.
- `scripts/`: SLURM submission scripts.
- `apptainer.def`: Apptainer definition file for the execution environment.
- `container.sif`: Built Apptainer image (after build).

## Environment Setup

The execution environment is managed via Apptainer (Singularity).

### 1. Build the Container and Setup Data

Submit the build job and run the reproducible setup script:

```bash
# Build the Apptainer container
sbatch scripts/build_container.sh

# Run the reproducible setup (extract and patch author code/data)
bash scripts/setup_repro.sh
```

Alternatively, if you have sufficient resources locally:

```bash
module load apptainer
apptainer build container.sif apptainer.def
```

## Running the Analysis

The analysis is computationally intensive and should be run on the cluster using SLURM.

### 1. Execute Analysis Pipeline

```bash
sbatch scripts/run_analysis.sh
```

This script will:
1. Run routing computations (`routing_filters_nofilters.py`, `routing_filter_variations.py`).
2. Group results (`route_nr_group.py`).
3. Reproduce figures and tables (`no_filters.py`, `filter_variations.py`).

## Generating the Report

To render the reproducibility report:

```bash
cd report
quarto render report.qmd --to pdf
```
