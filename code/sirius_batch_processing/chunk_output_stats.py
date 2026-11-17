#!/usr/bin/env python3
"""
Summarize row counts for every TSV output file across all SIRIUS chunk *_out dirs.
Prints a pivot table (file × chunk) and flags outliers.

Usage:
    python chunk_output_stats.py \
        --root /path/to/sirius_batches \
        [--out  /path/to/sirius_merged/chunk_output_stats.tsv]
"""
import os, sys, glob, argparse
import pandas as pd

# Files to check — in the order we want them printed
TARGET_FILES = [
    "formula_identifications.tsv",
    "structure_identifications.tsv",
    "canopus_formula_summary.tsv",
    "canopus_structure_summary.tsv",
    "spectral_matches.tsv",
    "denovo_structure_identifications.tsv",
    "fingerprints.tsv",
    # top-10 variants
    "formula_identifications_top-10.tsv",
    "structure_identifications_top-10.tsv",
    "canopus_formula_summary-10.tsv",
    "denovo_structure_identifications_top-10.tsv",
    "spectral_matches_top-10.tsv",
]

OUTLIER_Z = 2.0   # flag if |z-score| > this (among chunks that have the file)


def count_rows(path: str) -> int:
    """Return data-row count (header excluded). Returns -1 if file unreadable."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            # skip header, count remaining lines (handles trailing newline)
            return sum(1 for line in fh) - 1
    except Exception:
        return -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True,
                    help="Directory containing *_out chunk subdirs")
    ap.add_argument("--out", default=None,
                    help="Optional path to save the stats table as TSV")
    args = ap.parse_args()

    chunk_dirs = sorted(
        d for d in glob.glob(os.path.join(args.root, "*_out"))
        if os.path.isdir(d)
    )
    if not chunk_dirs:
        print(f"No *_out directories found under {args.root}", file=sys.stderr)
        sys.exit(1)

    chunk_labels = [os.path.basename(d) for d in chunk_dirs]

    # Build records: {file: {chunk: row_count or None}}
    records = {}
    for fname in TARGET_FILES:
        records[fname] = {}
        for chunk_dir, label in zip(chunk_dirs, chunk_labels):
            path = os.path.join(chunk_dir, fname)
            if os.path.isfile(path):
                records[fname][label] = count_rows(path)
            else:
                records[fname][label] = None   # file missing

    df = pd.DataFrame(records, index=chunk_labels).T   # file × chunk
    df.index.name = "file"

    # ── Pretty-print pivot table ──────────────────────────────────────────────
    col_w = max(len(c) for c in chunk_labels) + 2
    file_w = max(len(f) for f in df.index) + 2

    header = f"{'file':<{file_w}}" + "".join(f"{c:>{col_w}}" for c in chunk_labels)
    print("\n" + header)
    print("-" * len(header))

    for fname, row in df.iterrows():
        vals = []
        for v in row:
            if v is None:
                vals.append(f"{'MISSING':>{col_w}}")
            elif v < 0:
                vals.append(f"{'ERROR':>{col_w}}")
            else:
                vals.append(f"{v:>{col_w},}")
        print(f"{fname:<{file_w}}" + "".join(vals))

    # ── Outlier detection ────────────────────────────────────────────────────
    print("\n── Outliers (|z| > {}) ──────────────────────────────────────".format(OUTLIER_Z))
    found_outlier = False
    for fname, row in df.iterrows():
        present = {chunk: v for chunk, v in row.items() if v is not None and v >= 0}
        if len(present) < 3:
            continue   # not enough data points for meaningful z-score
        counts = pd.Series(present, dtype=float)
        z = (counts - counts.mean()) / counts.std(ddof=1)
        outliers = z[z.abs() > OUTLIER_Z]
        for chunk, zval in outliers.items():
            direction = "LOW" if zval < 0 else "HIGH"
            print(f"  {direction:4s}  {fname}  {chunk}  "
                  f"rows={present[chunk]:,}  z={zval:+.2f}  mean={counts.mean():.0f}")
            found_outlier = True

    # Flag any missing files
    for fname, row in df.iterrows():
        missing = [c for c, v in row.items() if v is None]
        if missing:
            print(f"  MISS  {fname}  missing in: {', '.join(missing)}")
            found_outlier = True

    if not found_outlier:
        print("  None detected.")

    # ── Save TSV ──────────────────────────────────────────────────────────────
    if args.out:
        df.to_csv(args.out, sep="\t")
        print(f"\nSaved to {args.out}")


if __name__ == "__main__":
    main()
