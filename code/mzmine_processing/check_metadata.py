#!/usr/bin/env python3
"""
check_metadata.py — validate a project metadata file BEFORE running the
mzmine -> SIRIUS pipeline, and print a clear list of issues to fix.

Run this at the START of processing a project. It checks exactly the things the
batch-prep step (update_mzmine_batch.py) and the nf100 blank-subtraction batch
need, and nothing it reports as an ERROR should be ignored.

Usage:
    python3 check_metadata.py <metadata_file>
    python3 check_metadata.py <project_folder>        # finds metadata/<file>
    python3 check_metadata.py <metadata_file> --no-blank   # project has no blank on purpose

What it checks
--------------
ERRORS (block the run):
  * file is readable and has a header
  * a Sample_Type column exists
  * a file-locator column exists (Full_path, or filename resolvable with --resolve-dir)
  * every row has a non-empty Sample_Type that maps to sample / blank / standard
  * every referenced file exists on disk and ends in .mzML
WARNINGS (you should look, but may be intentional):
  * no Blank rows  -> the nf100 *blank-subtraction* batch has nothing to subtract
                      (use the no-blank batch, or add a blank). Silence with --no-blank.
  * duplicate file names (same mzML used twice)
  * Sample_Type values with unexpected capitalization/spelling

Exit code is 0 only if there are no ERRORS.
"""
import argparse, csv, os, sys, collections

RESERVED = {"sample", "blank", "standard"}


def find_metadata(arg):
    """Accept a file, or a project folder (look in <folder>/metadata/)."""
    if os.path.isfile(arg):
        return arg
    if os.path.isdir(arg):
        mdir = os.path.join(arg, "metadata")
        cands = []
        for d in (mdir, arg):
            if os.path.isdir(d):
                cands += [os.path.join(d, f) for f in sorted(os.listdir(d))
                          if f.lower().endswith((".csv", ".txt", ".tsv"))]
        if len(cands) == 1:
            return cands[0]
        if not cands:
            sys.exit(f"ERROR: no .csv/.txt/.tsv metadata file found under {arg}")
        sys.exit("ERROR: multiple metadata files found; pass one explicitly:\n  "
                 + "\n  ".join(cands))
    sys.exit(f"ERROR: not a file or folder: {arg}")


def load(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        head = f.read(8192)
        f.seek(0)
        delim = "\t" if head.count("\t") > head.count(",") else ","
        rows = list(csv.DictReader(f, delimiter=delim))
    return rows, delim


def col(cols, *names):
    """Case/space-insensitive column lookup; returns actual header or None."""
    want = {n.lower() for n in names}
    for c in cols:
        if c.strip().lower() in want:
            return c
    return None


def main():
    ap = argparse.ArgumentParser(description="Validate a project metadata file for the mzmine/SIRIUS pipeline.")
    ap.add_argument("target", help="metadata file, or a <project>_mzmine_sirius folder")
    ap.add_argument("--resolve-dir", help="directory of converted .mzML; resolve by filename instead of Full_path")
    ap.add_argument("--ext", default=".mzML", help="converted-file extension (default .mzML)")
    ap.add_argument("--no-blank", action="store_true", help="this project intentionally has no blank (silence that warning)")
    ap.add_argument("--max-examples", type=int, default=5)
    args = ap.parse_args()

    path = find_metadata(args.target)
    print(f"Checking: {path}")
    rows, delim = load(path)
    print(f"  format: {'TAB' if delim == chr(9) else 'COMMA'}-delimited | data rows: {len(rows)}")

    errors, warnings = [], []
    if not rows:
        errors.append("file has no data rows")
        return report(path, errors, warnings)

    cols = list(rows[0].keys())
    c_st = col(cols, "Sample_Type")
    c_fp = col(cols, "Full_path")
    c_fn = col(cols, "filename", "file_name")

    # --- required columns ---
    if not c_st:
        errors.append("missing required column 'Sample_Type'")
    if not c_fp and not (args.resolve_dir and c_fn):
        errors.append("missing a file locator: need a 'Full_path' column "
                      "(or a 'filename' column together with --resolve-dir)")

    # --- Sample_Type values ---
    if c_st:
        st = collections.Counter((r.get(c_st) or "").strip() for r in rows)
        empties = st.pop("", 0)
        print(f"  Sample_Type: {dict(st)}" + (f"  (+{empties} EMPTY)" if empties else ""))
        if empties:
            errors.append(f"{empties} row(s) have an empty Sample_Type")
        unexpected = [v for v in st if v.lower() not in RESERVED]
        if unexpected:
            warnings.append(f"Sample_Type has non-standard value(s) {unexpected}; "
                            f"expected Sample / Blank / Standard (case-insensitive)")
        if not any(v.lower() == "blank" for v in st) and not args.no_blank:
            warnings.append("no Blank rows -> the nf100 blank-subtraction batch has nothing to "
                            "subtract. Use the no-blank batch, or add a blank. (--no-blank to silence)")

    # --- file existence ---
    if c_fp or (args.resolve_dir and c_fn):
        existing = {}
        if args.resolve_dir:
            existing = {p for p in os.listdir(args.resolve_dir)} if os.path.isdir(args.resolve_dir) else set()
        miss, nonmzml, empty, seen = [], 0, 0, collections.Counter()
        missing_dirs = collections.Counter()
        for i, r in enumerate(rows, 1):
            if args.resolve_dir and c_fn:
                fn = (r.get(c_fn) or "").strip()
                if not fn:
                    empty += 1; continue
                if not fn.lower().endswith(args.ext.lower()):
                    fn = fn + args.ext
                seen[fn] += 1
                if fn not in existing:
                    miss.append((i, os.path.join(args.resolve_dir, fn)))
            else:
                p = (r.get(c_fp) or "").strip()
                if not p:
                    empty += 1; continue
                seen[os.path.basename(p)] += 1
                if not p.lower().endswith(".mzml"):
                    nonmzml += 1
                if not os.path.exists(p):
                    miss.append((i, p))
                    missing_dirs[os.path.dirname(p)] += 1
        total = len(rows)
        print(f"  files: {total - len(miss) - empty}/{total} found"
              + (f" | {len(miss)} MISSING" if miss else "")
              + (f" | {empty} empty path" if empty else "")
              + (f" | {nonmzml} not .mzML" if nonmzml else ""))
        if empty:
            errors.append(f"{empty} row(s) have an empty file path/name")
        if nonmzml:
            errors.append(f"{nonmzml} path(s) do not end in .mzML (batch needs converted .mzML)")
        if miss:
            errors.append(f"{len(miss)} referenced file(s) do not exist on disk")
            # group missing by directory -> usually one wrong/typo'd folder explains many
            if missing_dirs:
                print("    missing files group by directory (a whole missing dir is usually a typo'd path):")
                for d, n in missing_dirs.most_common(args.max_examples):
                    tag = "DIR-NOT-FOUND" if not os.path.isdir(d) else "dir-ok,file-missing"
                    print(f"      [{tag}] {n:>4}  {d}")
            for i, p in miss[:args.max_examples]:
                print(f"      row {i}: {p}")
            if len(miss) > args.max_examples:
                print(f"      ... and {len(miss) - args.max_examples} more")
        dups = {k: v for k, v in seen.items() if v > 1}
        if dups:
            warnings.append(f"{len(dups)} file name(s) used in more than one row (e.g. "
                            f"{list(dups)[:3]})")

    return report(path, errors, warnings)


def report(path, errors, warnings):
    print()
    for w in warnings:
        print(f"  ⚠ WARNING: {w}")
    for e in errors:
        print(f"  ✗ ERROR:   {e}")
    print()
    if errors:
        print(f"RESULT: NOT READY — {len(errors)} error(s), {len(warnings)} warning(s). Fix errors, re-run this check.")
        sys.exit(1)
    if warnings:
        print(f"RESULT: USABLE WITH WARNINGS — 0 errors, {len(warnings)} warning(s). Review the warnings above.")
        sys.exit(0)
    print("RESULT: READY ✓ — no issues found.")
    sys.exit(0)


if __name__ == "__main__":
    main()
