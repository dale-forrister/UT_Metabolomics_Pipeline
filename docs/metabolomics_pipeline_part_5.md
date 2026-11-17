# <div align="center"> Part 5: Batch Processing SIRIUS at Scale </div>

[← Back to Main README](../README.md)

## Table of Contents
  - [Overview](#overview)
  - [Code used in this step](#code-used-in-this-step)
  - [Step 1: Split the MGF into chunks](#step-1-split-the-mgf-into-chunks)
  - [Step 2: Run SIRIUS on each chunk](#step-2-run-sirius-on-each-chunk)
  - [Step 3: Extract predicted fingerprints per chunk](#step-3-extract-predicted-fingerprints-per-chunk)
  - [Step 4: Merge chunk exports back together](#step-4-merge-chunk-exports-back-together)
  - [Optional: QC row-count stats across chunks](#optional-qc-row-count-stats-across-chunks)
  - [Scaling across multiple nodes](#scaling-across-multiple-nodes)

## Overview

[Part 4](metabolomics_pipeline_part_4.md) shows how to run SIRIUS on a single MGF file. For a full project, the MGF is usually too large (tens of thousands of features) to run through SIRIUS in one shot — memory blows up and a single failed feature can stall the whole run. Instead we:

1. Split the project MGF into fixed-size chunks.
2. Run the full SIRIUS CLI pipeline (formulas → zodiac → fingerprint → canopus → structures → denovo-structures → summaries) on each chunk independently, with a `.done` marker per chunk so the run is resumable and can be split across nodes.
3. Extract the predicted CSI:FingerID fingerprint bits per feature from each finished chunk's `.sirius` project space (these aren't included in the plain-text summary TSVs — they have to be pulled out via the SIRIUS REST API/PySirius).
4. Merge everything (summary TSVs + fingerprints) back into one project-level `sirius_merged/` folder.

## Code used in this step

All scripts referenced below live in [`code/sirius_batch_processing/`](../code/sirius_batch_processing/):

| Script | Purpose |
|---|---|
| `split_mgf_randomized.py` | Splits a project MGF into shuffled, fixed-size chunk MGFs |
| `run_sirius_batches.sh` | Runs the SIRIUS CLI pipeline on every chunk, with resume-via-`.done` support |
| `extract_sirius_fingerprints_V2.py` | Pulls the predicted fingerprint bits per feature out of each finished chunk's SIRIUS project space |
| `merge_sirius_exports_V2.py` | Stacks all chunks' summary TSVs and fingerprint matrices back into one merged output folder |
| `chunk_output_stats.py` | Optional QC — row counts per output file per chunk, flags chunks that look like outliers or are missing files |

## Step 1: Split the MGF into chunks

```bash
conda activate /stor/work/Sedio/conda_envs/mzmine_processing

python code/sirius_batch_processing/split_mgf_randomized.py \
  -i /path/to/project_sirius.mgf \
  -o /path/to/sirius_batches \
  --max-features 10000 \
  --prefix my_project_sirius_chunk \
  --drop-charge2
```

- `--max-features` controls chunk size (10,000 features/chunk works well in practice).
- `--drop-charge2` drops `CHARGE=2+` blocks, which SIRIUS doesn't handle.
- Feature groups are shuffled before chunking, so chunk runtimes stay roughly even instead of clustering all the slow/complex features into one chunk.

This produces `my_project_sirius_chunk_0001.mgf`, `_0002.mgf`, etc. in the output directory.

## Step 2: Run SIRIUS on each chunk

Use `screen` or `tmux` for this — chunk runs can take hours.

```bash
tmux new -s sirius
conda activate /stor/work/Sedio/conda_envs/sirius622

sirius login -u your_email@utexas.edu -p
# check status any time with: sirius login --show

code/sirius_batch_processing/run_sirius_batches.sh \
  --input-dir /path/to/sirius_batches \
  --prefix my_project_sirius_chunk \
  --sirius-bin /stor/work/Sedio/software/sirius_6.2.2/sirius/bin/sirius \
  --cores 18
```

Each chunk gets its own `<chunk_id>_out/` folder plus a `.sirius` project space, a per-chunk log under `sirius_batches/logs/`, and everything is also appended to `sirius_batches/logs/master.log`. A chunk that finishes successfully gets a `.done` marker inside its `_out` folder — chunks that already have one are skipped, so you can safely re-run this script to resume after an interruption or to pick up new chunks.

To run only specific chunks (e.g. splitting work across two nodes at once), pass `--chunks`:

```bash
# Node A
code/sirius_batch_processing/run_sirius_batches.sh --input-dir ... --prefix ... --sirius-bin ... --chunks 0001,0002,0003

# Node B (separate session, running in parallel)
code/sirius_batch_processing/run_sirius_batches.sh --input-dir ... --prefix ... --sirius-bin ... --chunks 0004,0005,0006
```

## Step 3: Extract predicted fingerprints per chunk

The fingerprint bit vectors aren't written to any of the summary TSVs — they have to be pulled per-feature out of the `.sirius` project space via PySirius. Run this after a chunk's `.done` marker appears:

```bash
conda activate /stor/work/Sedio/conda_envs/sirius622
sirius login -u your_email@utexas.edu -p   # if not already logged in this shell

python -u code/sirius_batch_processing/extract_sirius_fingerprints_V2.py \
  --projects /path/to/sirius_batches/my_project_sirius_chunk_0001_out \
  --sirius-path /stor/work/Sedio/software/sirius_6.2.2/sirius/bin/sirius \
  --port 8888 2>&1 | tee /path/to/sirius_batches/logs/fingerprint_log_chunk_0001.txt
```

Notes:
- Writes `fingerprints.tsv` (feature × fingerprint-bit matrix) inside the chunk's `_out` folder. Chunks that already have one are skipped, so this is safe to re-run.
- SIRIUS is started fresh and fully shut down (including killing anything on `--port`) for each `--projects` entry passed, so chunks are safe to process one after another on the same port.
- To process multiple chunks in one call, pass them all to `--projects`; to scan a whole batches directory for anything finished-but-not-yet-extracted, use `--projects-root /path/to/sirius_batches` instead.
- If running two extraction jobs concurrently (e.g. on two nodes), use a different `--port` for each so they don't collide.

## Step 4: Merge chunk exports back together

Once all chunks have both their SIRIUS summaries and their `fingerprints.tsv`:

```bash
mkdir -p /path/to/sirius_merged

python code/sirius_batch_processing/merge_sirius_exports_V2.py \
  --root /path/to/sirius_batches \
  --out  /path/to/sirius_merged
```

This is pure pandas — no conda env or SIRIUS login required. It does two things in one pass:

- Every summary TSV (`formula_identifications.tsv`, `canopus_formula_summary.tsv`, `structure_identifications.tsv`, `spectral_matches.tsv`, etc.) is merged by filename across all chunks, with a `batch` column added so each row can be traced back to its source chunk.
- `fingerprints.tsv` files are stacked into a single feature × fingerprint-bit matrix (no `batch` column — `feature_id` is the index), ready to feed into downstream distance/clustering calculations.

## Optional: QC row-count stats across chunks

Useful for spotting a chunk that silently produced far fewer hits than the others (formula search failures, truncated input, etc.):

```bash
python code/sirius_batch_processing/chunk_output_stats.py \
  --root /path/to/sirius_batches \
  --out  /path/to/sirius_merged/chunk_output_stats.tsv
```

Prints a file × chunk pivot table of row counts, flags any chunk missing an expected output file, and flags chunks whose row count for a given file is a statistical outlier (`|z| > 2`) relative to the other chunks.

## Scaling across multiple nodes

The whole workflow above is chunk-independent, so Steps 2 and 3 can be split across separate compute nodes/clusters running in parallel — just partition the chunk IDs between sessions (via `--chunks` for Step 2, or separate `--projects` lists for Step 3) and point every session at the same shared `sirius_batches` directory. Wait until every chunk has both a `.done` marker and a `fingerprints.tsv` before running Step 4's merge.
