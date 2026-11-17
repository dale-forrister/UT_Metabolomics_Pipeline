#!/usr/bin/env python3
"""
Merge SIRIUS batch exports across chunk *_out directories.

Two modes in one pass:
  - fingerprints.tsv  : pure feature × fingerprint matrix (feature_id as index,
                        no batch column).  Rows are simply stacked across chunks.
  - all other TSVs    : generic merge by filename with a 'batch' column added so
                        each row can be traced back to its source chunk.

Usage:
    python merge_sirius_exports_V2.py \
        --root  /path/to/sirius_batches \
        --out   /path/to/sirius_merged
"""
import os, sys, glob, argparse, csv
import pandas as pd


def read_tsv(path: str) -> pd.DataFrame:
    # SIRIUS summary TSVs can contain stray literal double-quote characters
    # in free-text fields (e.g. compound names). These aren't CSV quoting,
    # so disable quote handling entirely -- otherwise an odd number of quote
    # chars makes pandas treat the rest of the file as one unterminated
    # quoted field and raise "EOF inside string".
    return pd.read_csv(path, sep="\t", dtype=str, low_memory=False, quoting=csv.QUOTE_NONE)


def merge_summaries(root: str, out_dir: str) -> None:
    """Merge every TSV (except fingerprints.tsv) found under *_out dirs."""
    summary_files = [
        f for f in glob.glob(os.path.join(root, "*_out", "*.tsv"), recursive=False)
        if os.path.basename(f) != "fingerprints.tsv"
    ]

    by_base: dict[str, list[str]] = {}
    for f in summary_files:
        by_base.setdefault(os.path.basename(f), []).append(f)

    for base, paths in sorted(by_base.items()):
        print(f"Merging {base}  ({len(paths)} chunks)")
        dfs = []
        for p in sorted(paths):
            batch = os.path.basename(os.path.dirname(p))
            try:
                df = read_tsv(p)
            except Exception as e:
                print(f"  ! Skipping {p}: {e}", file=sys.stderr)
                continue
            df.insert(0, "batch", batch)
            dfs.append(df)

        if not dfs:
            print(f"  ! No readable parts for {base}", file=sys.stderr)
            continue

        # Union of columns across all chunks
        all_cols = list(dict.fromkeys(c for df in dfs for c in df.columns))
        aligned = []
        for df in dfs:
            for c in all_cols:
                if c not in df.columns:
                    df[c] = pd.NA
            aligned.append(df[all_cols])

        merged = pd.concat(aligned, ignore_index=True, sort=False)
        out_path = os.path.join(out_dir, base)
        merged.to_csv(out_path, sep="\t", index=False)
        print(f"  -> {out_path}  [{len(merged)} rows]")


def merge_fingerprints(root: str, out_dir: str) -> None:
    """Stack fingerprints.tsv files from all chunks into one matrix."""
    fp_files = sorted(glob.glob(os.path.join(root, "*_out", "fingerprints.tsv")))

    if not fp_files:
        print("No fingerprints.tsv files found — skipping fingerprint merge.", file=sys.stderr)
        return

    print(f"Merging fingerprints.tsv  ({len(fp_files)} chunks)")
    dfs = []
    for p in fp_files:
        try:
            df = pd.read_csv(p, sep="\t", index_col="feature_id", dtype=str, low_memory=False)
            dfs.append(df)
            print(f"  read {len(df)} features from {os.path.basename(os.path.dirname(p))}")
        except Exception as e:
            print(f"  ! Skipping {p}: {e}", file=sys.stderr)

    if not dfs:
        print("  ! No readable fingerprints.tsv parts", file=sys.stderr)
        return

    merged = pd.concat(dfs, axis=0, sort=False)
    out_path = os.path.join(out_dir, "fingerprints.tsv")
    merged.to_csv(out_path, sep="\t", index=True)
    print(f"  -> {out_path}  [{len(merged)} features × {merged.shape[1]} bits]")


def main():
    ap = argparse.ArgumentParser(
        description="Merge SIRIUS chunk exports (summaries + fingerprints) into one folder."
    )
    ap.add_argument("--root", required=True,
                    help="Directory containing chunk *_out subdirs (e.g. sirius_batches)")
    ap.add_argument("--out", required=True,
                    help="Output directory for merged files (e.g. sirius_merged)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    merge_summaries(args.root, args.out)
    merge_fingerprints(args.root, args.out)

    print("\nDone.")


if __name__ == "__main__":
    main()
