#!/usr/bin/env bash
# Run SIRIUS on every chunk_*.mgf file produced by split_mgf_randomized.py.
#
# - Resumable: writes a .done marker inside each chunk's *_out dir; chunks
#   with a .done marker are skipped on re-run.
# - Logs: per-chunk log under <input-dir>/logs/, plus a combined master.log.
# - Safe to split TARGET_CHUNKS across multiple nodes/clusters by running this
#   script with a filtered chunk list (see --chunks below).
#
# Requires: conda env sirius622 active, and `sirius login` already run in
# this shell (see docs/metabolomics_pipeline_part_5.md).
#
# Usage:
#   ./run_sirius_batches.sh \
#     --input-dir /path/to/sirius_batches \
#     --prefix my_project_sirius_chunk \
#     --sirius-bin /stor/work/Sedio/software/sirius_6.2.2/sirius/bin/sirius \
#     --cores 18
#
#   # Only run specific chunk numbers (e.g. to split work across nodes):
#   ./run_sirius_batches.sh --input-dir ... --prefix ... --sirius-bin ... \
#     --chunks 0006,0007,0008

set -euo pipefail

CORES=18
INSTRUMENT="orbitrap"
CANDIDATES=10
PPM_MS2=10
DB_LIST="pubchem,metacyc,bio,chebi,gnps,hmdb,hsdb,kegg,knapsack,lotus,lipidmaps,maconda,mesh,mimedb,norman,plantcyc,pubchemannotationbio,pubchemannotationdrug,pubchemannotationfood,pubchemannotationsafetyandtoxic,pubmed,supernatural,teromol,ymdb"
CHUNKS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input-dir) INPUT_DIR="$2"; shift 2 ;;
    --prefix) PREFIX="$2"; shift 2 ;;
    --sirius-bin) SIRIUS_BIN="$2"; shift 2 ;;
    --cores) CORES="$2"; shift 2 ;;
    --chunks) CHUNKS="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

: "${INPUT_DIR:?--input-dir required}"
: "${PREFIX:?--prefix required}"
: "${SIRIUS_BIN:?--sirius-bin required}"

OUTPUT_DIR="$INPUT_DIR"
LOG_DIR="${OUTPUT_DIR}/logs"
MASTER_LOG="${LOG_DIR}/master.log"
DONE_MARKER_NAME=".done"
mkdir -p "$LOG_DIR"

ts_now() { date '+%Y-%m-%d %H:%M:%S %Z'; }
secs()   { date +%s; }

echo "==== RUN START $(ts_now) ====" | tee -a "$MASTER_LOG"

if [[ -n "$CHUNKS" ]]; then
  IFS=',' read -ra chunk_nums <<< "$CHUNKS"
  chunks=()
  for n in "${chunk_nums[@]}"; do
    chunks+=( "${INPUT_DIR}/${PREFIX}_${n}.mgf" )
  done
else
  shopt -s nullglob
  chunks=( "${INPUT_DIR}"/${PREFIX}_*.mgf )
  shopt -u nullglob
fi

if (( ${#chunks[@]} == 0 )); then
  echo "No input files matching ${INPUT_DIR}/${PREFIX}_*.mgf" | tee -a "$MASTER_LOG"
  exit 1
fi

for mgf in "${chunks[@]}"; do
  if [[ ! -f "$mgf" ]]; then
    echo "[$(ts_now)] MISSING ${mgf} — skipping" | tee -a "$MASTER_LOG"
    continue
  fi

  base="$(basename "$mgf")"
  chunk_id="${base%.mgf}"
  out_dir="${OUTPUT_DIR}/${chunk_id}_out"
  per_log="${LOG_DIR}/${chunk_id}.log"
  done_marker="${out_dir}/${DONE_MARKER_NAME}"

  if [[ -e "$done_marker" ]]; then
    echo "[$(ts_now)] SKIP ${chunk_id} (found ${done_marker})" | tee -a "$MASTER_LOG"
    continue
  fi

  cmd=( "$SIRIUS_BIN" --cores="$CORES"
        -i "$mgf"
        -o "$out_dir"
        spectra-search
        formulas -p "$INSTRUMENT" -c "$CANDIDATES" -I "[M+H]+" -i "[M+Na]+,[M+K]+" --ppm-max 5 --ppm-max-ms2 "$PPM_MS2"
        zodiac
        fingerprint
        canopus
        structures --db "$DB_LIST"
        denovo-structures
        write-summaries --top-k-summary 10
  )

  start_wall=$(ts_now)
  start_secs=$(secs)

  {
    echo "=============================="
    echo "CHUNK:     ${chunk_id}"
    echo "INPUT:     ${mgf}"
    echo "OUTPUT:    ${out_dir}"
    echo "START:     ${start_wall}"
    echo "CORES:     ${CORES}"
    echo "COMMAND:   ${cmd[*]}"
    echo "------------------------------"
  } | tee -a "$per_log" "$MASTER_LOG"

  if "${cmd[@]}" 2>&1 | tee -a "$per_log" "$MASTER_LOG"; then
    status=0
  else
    status=$?
  fi

  end_wall=$(ts_now)
  end_secs=$(secs)
  dur=$(( end_secs - start_secs ))

  {
    echo "STATUS:    ${status}"
    echo "END:       ${end_wall}"
    echo "DURATION:  ${dur}s"
    echo "=============================="
    echo
  } | tee -a "$per_log" "$MASTER_LOG"

  if [[ $status -eq 0 ]]; then
    : > "$done_marker"
  else
    echo "ERROR: chunk ${chunk_id} failed (exit ${status}). Continuing..." | tee -a "$MASTER_LOG"
  fi

done

echo "==== RUN END $(ts_now) ====" | tee -a "$MASTER_LOG"
