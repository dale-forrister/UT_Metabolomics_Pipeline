#!/usr/bin/env python3
"""
Update an MZmine .mzbatch to match a sample list.

What it does
------------
1. Rebuilds the "Import MS data" file list from the metadata (one <file> per row,
   taken from the mzML-path column; default: Converted_Path_Pod).
2. Generates an MZmine-format sample-metadata TSV (filename, mzmine_sample_type,
   + descriptive columns) from the sample list and points the import step at it.
   - mzmine_sample_type is lowercase (sample/blank/standard) so the BY_METADATA
     blank-subtraction step (column="mzmine_sample_type", group="blank") works.
3. Updates the spectral-library import step with --library path(s).
4. Relocates ALL output files into --output_dir and renames them, replacing the
   old batch stem (e.g. "v2_final_final") with --project_name.
5. Leaves the BY_METADATA blank step untouched (it's driven by the metadata).
6. Applies any --path-sub OLD::NEW remaps (use this for DreaMS / MS2DeepScore
   model paths once you add those steps back in), then warns about any leftover
   foreign absolute paths (e.g. /Users/...) it did not rewrite.

Example
-------
python3 update_mzmine_batch.py \
  --mzbatch   v2_final_final.mzbatch \
  --metadata  ../data/Panama_metadata_20261106.csv \
  --output_dir ../mzmine_output \
  --project_name Panama \
  --library   ../libraries/UT_Austin_in_house_V2_cocktailRT_20261031.json
"""

import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Output files that get relocated into output_dir and re-stemmed.
OUTPUT_EXTS = {".mgf", ".graphml", ".csv", ".mzbatch"}

# Metadata columns to carry into the mzmine metadata file (source -> mzmine header).
# Only columns present in the CSV are written. filename + mzmine_sample_type are
# always written first.
EXTRA_COLS = {
    "Sample_Name": "sample_name",
    "Family": "family",
    "Genus": "genus",
    "Species": "species",
    "Plate_Position": "plate_position",
    "Order_#": "order",
    "Date": "date",
}

# Sample_Type -> mzmine_sample_type (reserved values are lowercase).
SAMPLE_TYPE_MAP = {
    "sample": "sample",
    "blank": "blank",
    "standard": "standard",
    "qc": "qc",
}


def load_metadata(metadata_path, path_col, require_path=True):
    with open(metadata_path, newline="") as fh:
        # sniff delimiter
        sample = fh.read(8192)
        fh.seek(0)
        delim = "\t" if sample.count("\t") > sample.count(",") else ","
        rows = list(csv.DictReader(fh, delimiter=delim))
    if not rows:
        sys.exit(f"ERROR: no data rows in {metadata_path}")
    cols = rows[0].keys()
    if "Sample_Type" not in cols:
        sys.exit("ERROR: metadata has no 'Sample_Type' column.")
    if require_path:
        if path_col not in cols:
            sys.exit(f"ERROR: path column '{path_col}' not found. Available: {list(cols)}")
        # keep only rows that actually have a path
        rows = [r for r in rows if (r.get(path_col) or "").strip()]
    return rows


def resolve_files(rows, resolve_dir, ext):
    """Resolve each metadata row to the ACTUAL converted file in resolve_dir.
    The converter names samples '<Mnemonic>_<SampleID><ext>' and blanks/standards
    just '<Sample_Name><ext>', so the metadata's path column is ignored here.
    Returns (matched_rows, missing_list). Matched rows gain _resolved_name/_resolved_path."""
    resolve_dir = Path(resolve_dir)
    existing = {p.name for p in resolve_dir.glob(f"*{ext}")}
    sid_col = next((c for c in rows[0] if c.strip().lower().startswith("sampleid")), None)
    matched, missing = [], []
    for r in rows:
        mn = (r.get("Mnemonic") or "").strip()
        sid = (r.get(sid_col) or "").strip() if sid_col else ""
        sn = (r.get("Sample_Name") or "").strip()
        cands = []
        if mn and sid:
            cands.append(f"{mn}_{sid}{ext}")
        if sn:
            cands.append(f"{sn}{ext}")
        hit = next((c for c in cands if c in existing), None)
        if hit:
            r["_resolved_name"] = hit
            r["_resolved_path"] = str((resolve_dir / hit).resolve())
            matched.append(r)
        else:
            missing.append((r.get("Sample_Type"), sn, mn, sid, cands))
    return matched, missing


def write_mzmine_metadata(rows, path_col, out_path):
    """Write an MZmine-compatible metadata TSV. Returns (path, warnings)."""
    warnings = []
    present_extra = [(src, dst) for src, dst in EXTRA_COLS.items() if src in rows[0]]
    header = ["filename", "mzmine_sample_type"] + [dst for _, dst in present_extra]

    seen = {}
    out_rows = []
    for r in rows:
        fname = r.get("_resolved_name") or Path((r.get(path_col) or "").strip()).name
        raw_type = (r.get("Sample_Type") or "").strip().lower()
        mz_type = SAMPLE_TYPE_MAP.get(raw_type)
        if mz_type is None:
            mz_type = raw_type or "sample"
            warnings.append(f"unmapped Sample_Type '{r.get('Sample_Type')}' -> '{mz_type}' ({fname})")
        line = [fname, mz_type] + [(r.get(src) or "").strip() for src, _ in present_extra]
        out_rows.append(line)
        seen[fname] = seen.get(fname, 0) + 1

    dupes = {f: n for f, n in seen.items() if n > 1}
    if dupes:
        warnings.append(f"DUPLICATE filenames in metadata (mzmine matches by filename!): {dupes}")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(out_rows)

    n_blank = sum(1 for l in out_rows if l[1] == "blank")
    print(f"  metadata: {len(out_rows)} files -> {out_path}  (blanks tagged: {n_blank})")
    return str(out_path), warnings


def _restem_output(path_str, output_dir, old_stem, project_name):
    """Return new absolute path for an output file: relocate + swap stem."""
    fname = Path(path_str).name
    if old_stem and old_stem in fname:
        fname = fname.replace(old_stem, project_name)
    elif "mzmine_output_" in fname:
        fname = fname.replace("mzmine_output_", f"{project_name}_")
    elif not fname.startswith(f"{project_name}_"):
        fname = f"{project_name}_{fname}"
    return str(Path(output_dir) / fname)


def _is_pathlike(s):
    return bool(s) and ("/" in s or "\\" in s)


def detect_output_stem(root):
    """Figure out the common output filename stem (e.g. 'v2_final_final' or
    'LCMS_Analysis_Standard_Cocktail_V3'), which is usually NOT the .mzbatch
    filename. Strategy: use the autosave '<stem>_batch.mzbatch' name if present,
    else the longest common prefix of all output basenames."""
    # 1) autosave batch filename
    for step in root.findall(
        ".//batchstep[@method='io.github.mzmine.modules.batchmode.autosave.AutoSaveBatchModule']"
    ):
        cf = step.find(".//current_file")
        if cf is not None and cf.text:
            name = Path(cf.text).name
            if name.endswith("_batch.mzbatch"):
                return name[: -len("_batch.mzbatch")]
    # 2) longest common prefix of output-extension basenames
    names = []
    for elem in root.iter():
        t = elem.text
        if _is_pathlike(t) and Path(t.strip()).suffix.lower() in OUTPUT_EXTS:
            names.append(Path(t.strip()).name)
    if names:
        import os
        lcp = os.path.commonprefix(names).rstrip("_")
        if len(lcp) >= 3:
            return lcp
    return None


def update_mzbatch(args):
    tree = ET.parse(args.mzbatch)
    root = tree.getroot()

    rows = load_metadata(args.metadata, args.path_col, require_path=not args.resolve_dir)
    if args.resolve_dir:
        rows, missing = resolve_files(rows, args.resolve_dir, args.resolve_ext)
        print(f"  resolved {len(rows)} files in {args.resolve_dir} "
              f"(ext {args.resolve_ext}); unmatched metadata rows: {len(missing)}")
        for m in missing[:12]:
            print(f"    UNMATCHED: type={m[0]} sample_name={m[1]} mnemonic={m[2]} "
                  f"sampleid={m[3]} tried={m[4]}")
        if not rows:
            sys.exit("ERROR: no files resolved in --resolve_dir; check the directory/extension.")
        # de-dupe: multiple metadata rows can resolve to the same file (replicate
        # rows / data-entry dupes). mzmine imports+matches by filename, so keep one.
        seen, uniq, collapsed = set(), [], []
        for r in rows:
            n = r["_resolved_name"]
            if n in seen:
                collapsed.append(n)
                continue
            seen.add(n)
            uniq.append(r)
        if collapsed:
            print(f"  de-duped {len(collapsed)} duplicate-filename rows -> {len(uniq)} unique files: "
                  f"{sorted(set(collapsed))}")
        rows = uniq
        mzml_paths = [r["_resolved_path"] for r in rows]
    else:
        mzml_paths = [r[args.path_col].strip() for r in rows]

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- generate mzmine metadata ---
    meta_out = Path(args.mzmine_metadata).resolve() if args.mzmine_metadata \
        else (output_dir / f"{args.project_name}_mzmine_metadata.tsv")
    meta_path, meta_warnings = write_mzmine_metadata(rows, args.path_col, meta_out)

    old_stem = args.old_stem or detect_output_stem(root) or Path(args.mzbatch).stem
    print(f"  output stem detected: '{old_stem}' -> '{args.project_name}'")

    # --- 1. Import MS data: file list + metadata file ---
    n_import = 0
    for step in root.findall(
        ".//batchstep[@method='io.github.mzmine.modules.io.import_rawdata_all.AllSpectralDataImportModule']"
    ):
        n_import += 1
        files_param = step.find(".//parameter[@name='File names']")
        if files_param is not None:
            for f in list(files_param.findall("file")):
                files_param.remove(f)
            for p in mzml_paths:
                el = ET.SubElement(files_param, "file")
                el.text = p
        meta_param = step.find(".//parameter[@name='Metadata file']")
        if meta_param is not None:
            for tag in ("current_file", "last_file"):
                el = meta_param.find(tag)
                if el is None:
                    el = ET.SubElement(meta_param, tag)
                el.text = str(meta_path)
            meta_param.set("selected", "true")
    print(f"  import steps updated: {n_import}  ({len(mzml_paths)} mzML files)")

    # --- 2. Spectral library import ---
    n_lib = 0
    if args.library:
        for step in root.findall(
            ".//batchstep[@method='io.github.mzmine.modules.io.import_spectral_library.SpectralLibraryImportModule']"
        ):
            lib_param = step.find(".//parameter[@name='Spectral library files']")
            if lib_param is not None:
                for f in list(lib_param.findall("file")):
                    lib_param.remove(f)
                for lib in args.library:
                    el = ET.SubElement(lib_param, "file")
                    el.text = str(Path(lib).resolve())
                    n_lib += 1
        print(f"  spectral library files set: {n_lib}")
    else:
        print("  WARNING: no --library given; library import step left as-is (likely a Mac path).")

    # --- 2b. DreaMS / MS2Deepscore model files (spectral networking steps) ---
    # Rewrite by parameter name so it's independent of the old (Mac) path.
    MODEL_PARAMS = ("MS2Deepscore model", "DreaMS model")
    n_models = 0
    missing_models = []
    for step in root.findall(
        ".//batchstep[@method='io.github.mzmine.modules.dataprocessing.group_spectral_networking.MainSpectralNetworkingModule']"
    ):
        for pname in MODEL_PARAMS:
            mp = step.find(f".//parameter[@name='{pname}']")
            if mp is None:
                continue
            cf = mp.find("current_file")
            if cf is None or not (cf.text and cf.text.strip()):
                continue  # this algorithm isn't the selected one / no model set
            basename = Path(cf.text.strip()).name
            if args.model_dir:
                new = str((Path(args.model_dir).resolve() / basename))
                for tag in ("current_file", "last_file"):
                    el = mp.find(tag)
                    if el is not None:
                        el.text = new
                    if el is not None and "relative_path" in el.attrib:
                        el.set("relative_path", basename)
                if not Path(new).exists():
                    missing_models.append(new)
                n_models += 1
    if args.model_dir:
        print(f"  model files repointed to {args.model_dir}: {n_models}")
        for m in missing_models:
            print(f"    WARNING: model file not found on disk: {m}")

    # --- 3. Blank subtraction: verify it's metadata-driven ---
    for step in root.findall(
        ".//batchstep[@method='io.github.mzmine.modules.dataprocessing.filter_blanksubtraction.FeatureListBlankSubtractionModule']"
    ):
        bp = step.find(".//parameter[@name='Blank/Control raw data files']")
        if bp is not None and bp.get("type") == "BY_METADATA":
            print("  blank subtraction: BY_METADATA (driven by mzmine_sample_type=blank) - OK")
        elif bp is not None:
            print(f"  WARNING: blank step type is '{bp.get('type')}', not BY_METADATA; "
                  "blanks are NOT driven by the metadata file. Check this step in the GUI.")

    # --- 4. Arbitrary path substitutions (e.g. DreaMS / MS2DeepScore models) ---
    subs = []
    for s in (args.path_sub or []):
        if "::" not in s:
            sys.exit(f"ERROR: --path-sub must be OLD::NEW, got '{s}'")
        old, new = s.split("::", 1)
        subs.append((old, new))

    def apply_subs(text):
        for old, new in subs:
            if old in text:
                text = text.replace(old, new)
        return text

    # --- 5. Global sweep: relocate/rename outputs, apply subs, flag leftovers ---
    # An "output" is any path whose basename carries the old stem (covers
    # extension-less bases like the GNPS '..._iimn_gnps'); also fall back to
    # known output extensions. relative_path attrs are synced to the new base.
    def is_output_path(s):
        if not _is_pathlike(s):
            return False
        base = Path(s).name
        if old_stem and old_stem in base:
            return True
        return Path(s).suffix.lower() in OUTPUT_EXTS

    leftovers = set()
    for elem in root.iter():
        if elem.text and elem.text.strip():
            t = apply_subs(elem.text.strip())
            if is_output_path(t):
                t = _restem_output(t, output_dir, old_stem, args.project_name)
            elem.text = t
        # sync relative_path on the same element to the (new) basename
        if "relative_path" in elem.attrib and _is_pathlike(elem.text):
            elem.set("relative_path", Path(elem.text).name)
        for k, v in list(elem.attrib.items()):
            if not v or k == "relative_path":
                continue
            nv = apply_subs(v)
            if is_output_path(nv):
                nv = _restem_output(nv, output_dir, old_stem, args.project_name)
            elem.attrib[k] = nv

    # scan for foreign absolute paths we did not rewrite
    FOREIGN = ("/Users/", "C:\\", "C:/")
    for elem in root.iter():
        for val in ([elem.text] + list(elem.attrib.values())):
            if val and any(f in val for f in FOREIGN):
                leftovers.add(val.strip())

    # --- write ---
    out_batch = output_dir / f"{args.project_name}.mzbatch"
    tree.write(out_batch, encoding="UTF-8", xml_declaration=True)
    print(f"\n✅ Updated MZmine batch written to: {out_batch}")

    all_warnings = meta_warnings
    if all_warnings:
        print("\n⚠️  Metadata warnings:")
        for w in all_warnings:
            print(f"   - {w}")
    if leftovers:
        print("\n⚠️  Foreign absolute paths still in the batch (fix with --path-sub OLD::NEW or --library):")
        for lv in sorted(leftovers):
            print(f"   - {lv}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mzbatch", required=True)
    ap.add_argument("--metadata", required=True, help="Sample list CSV/TSV")
    ap.add_argument("--output_dir", required=True, help="Dir for the new .mzbatch, metadata, and all outputs")
    ap.add_argument("--project_name", required=True, help="Prefix for outputs; replaces the old batch stem")
    ap.add_argument("--path_col", default="Converted_Path_Pod", help="Metadata column with mzML paths "
                                                                      "(ignored when --resolve_dir is set)")
    ap.add_argument("--resolve_dir", help="Directory of converted files; resolve each metadata row to the real "
                                          "file by '<Mnemonic>_<SampleID><ext>' then '<Sample_Name><ext>', "
                                          "ignoring the (possibly stale) path column")
    ap.add_argument("--resolve_ext", default=".mzML", help="Extension to resolve in --resolve_dir (e.g. .mzML or .mzXML)")
    ap.add_argument("--library", nargs="+", help="Spectral library file(s) on the pod (.json/.mgf/...)")
    ap.add_argument("--model_dir", help="Directory holding the DreaMS / MS2Deepscore model files "
                                        "(the MS2Deepscore model + DreaMS model params are repointed "
                                        "to <model_dir>/<original basename>)")
    ap.add_argument("--mzmine_metadata", help="Where to write the generated mzmine metadata TSV "
                                              "(default: <output_dir>/<project>_mzmine_metadata.tsv)")
    ap.add_argument("--old_stem", help="Output filename stem to replace (default: .mzbatch basename)")
    ap.add_argument("--path-sub", dest="path_sub", action="append",
                    help="Remap a path substring: OLD::NEW (repeatable; for DreaMS/MS2DeepScore models etc.)")
    args = ap.parse_args()
    update_mzbatch(args)


if __name__ == "__main__":
    main()
