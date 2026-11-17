#!/usr/bin/env python3
"""
Extract predicted fingerprints from completed SIRIUS batch output directories.
Saves a fingerprints.tsv inside each *_out folder (one row per feature).
Skips chunks where fingerprints.tsv already exists.

SIRIUS is started fresh for each project and fully shut down after, avoiding
port-conflict failures when processing multiple chunks in sequence.

Requires PySirius (SIRIUS 6.x). Run inside the sirius622 conda env.
SIRIUS must already be logged in prior to running this script.

Usage:
    # Process an explicit list of chunks (e.g. to split across two pods):
    python extract_sirius_fingerprints_V2.py \
        --projects /path/chunk_0002_out /path/chunk_0003_out /path/chunk_0004_out \
        --sirius-path /path/to/sirius/bin/sirius

    # Or scan a directory for all completed (*_out + .done) chunks:
    python extract_sirius_fingerprints_V2.py \
        --projects-root /path/to/sirius_batches \
        --sirius-path /path/to/sirius/bin/sirius
"""
import os, sys, glob, argparse, time, subprocess
import hashlib
import pandas as pd
from PySirius import SiriusSDK, AlignedFeatureOptField


def kill_port(port):
    """Kill any process listening on the given TCP port before starting SIRIUS."""
    subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
    time.sleep(3)


def formula_exists(api, project_id, feature_id):
    try:
        api.features().get_aligned_feature(
            project_id, feature_id, [AlignedFeatureOptField.TOPANNOTATIONS]
        ).top_annotations.formula_annotation.formula_id
        return True
    except Exception:
        return False


def fingerprint_prediction_exists(api, project_id, feature_id, formula_id):
    try:
        api.features().get_fingerprint_prediction(project_id, feature_id, formula_id)
        return True
    except Exception:
        return False


def calculate_md5(value):
    md5 = hashlib.md5()
    md5.update(str(value).encode("utf-8"))
    return md5.hexdigest()


def process_chunk(out_dir, sirius_path, port):
    tag = os.path.basename(out_dir)
    sirius_proj = out_dir + ".sirius"
    out_path = os.path.join(out_dir, "fingerprints.tsv")

    print(f"\n{'='*60}")
    print(f"Processing {tag}")
    print(f"Project: {sirius_proj}")

    if os.path.isfile(out_path):
        print(f"  fingerprints.tsv already exists, skipping.")
        return

    if not os.path.exists(sirius_proj):
        print(f"  ! No matching .sirius project at {sirius_proj}, skipping.", file=sys.stderr)
        return

    # Kill any leftover process on this port before starting fresh
    kill_port(port)
    # Reset class-level SDK state so start_sirius() doesn't see the previous PID
    try:
        SiriusSDK.reset_sdk_class()
    except Exception:
        pass

    api = SiriusSDK().start_sirius(
        sirius_path=sirius_path,
        projectspace=os.path.abspath(sirius_proj),
        port=port,
        headless=True,
    )

    if api is None:
        print(f"  ! Failed to start SIRIUS for {tag}", file=sys.stderr)
        return

    time.sleep(10)

    try:
        project_id = api.projects().get_project_spaces()[0].project_id
        print(f"  project_id: {project_id}")

        features = api.features().get_aligned_features(project_id)
        print(f"  total features: {len(features)}")

        fingerprint_dict = {}
        for feature in features:
            feature_id = feature.aligned_feature_id
            name = feature.name
            if not formula_exists(api, project_id, feature_id):
                continue
            formula_id = (
                api.features()
                .get_aligned_feature(project_id, feature_id, [AlignedFeatureOptField.TOPANNOTATIONS])
                .top_annotations.formula_annotation.formula_id
            )
            if fingerprint_prediction_exists(api, project_id, feature_id, formula_id):
                fp = api.features().get_fingerprint_prediction(project_id, feature_id, formula_id)
                fingerprint_dict[name] = fp

        print(f"  features with fingerprints: {len(fingerprint_dict)}")

        # Deduplicate by MD5
        seen = {}
        for k, v in fingerprint_dict.items():
            m = calculate_md5(v)
            if m not in seen.values():
                seen[k] = m
        fingerprint_dict = {k: fingerprint_dict[k] for k in seen}
        print(f"  after dedup: {len(fingerprint_dict)}")

        if fingerprint_dict:
            fp_df = pd.DataFrame.from_dict(fingerprint_dict, orient="index")
            fp_df.index.name = "feature_id"
            fp_df.columns = [f"fp_{i}" for i in range(fp_df.shape[1])]
            fp_df.to_csv(out_path, sep="\t")
            print(f"  saved {fp_df.shape[0]} x {fp_df.shape[1]} -> {out_path}")
        else:
            print(f"  ! no fingerprints to save for {tag}", file=sys.stderr)

    except Exception as e:
        print(f"  ! error processing {tag}: {e}", file=sys.stderr)

    finally:
        try:
            api.shutdown()
        except Exception:
            pass
        time.sleep(5)
        kill_port(port)


def main():
    ap = argparse.ArgumentParser(
        description="Extract SIRIUS predicted fingerprints into each completed *_out project folder."
    )
    ap.add_argument("--projects", nargs="+",
                    help="Explicit list of *_out dirs to process (overrides --projects-root)")
    ap.add_argument("--projects-root",
                    help="Scan this directory for completed *_out dirs (requires .done marker)")
    ap.add_argument("--sirius-path", required=True, help="Path to sirius binary")
    ap.add_argument("--port", type=int, default=8888, help="SIRIUS REST server port (default: 8888)")
    args = ap.parse_args()

    if args.projects:
        out_dirs = [d.rstrip("/") for d in args.projects]
    elif args.projects_root:
        out_dirs = sorted([
            d for d in glob.glob(os.path.join(args.projects_root, "*_out"))
            if os.path.isfile(os.path.join(d, ".done"))
        ])
    else:
        print("ERROR: provide --projects or --projects-root", file=sys.stderr)
        sys.exit(1)

    if not out_dirs:
        print("No SIRIUS projects found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(out_dirs)} completed chunks")

    for out_dir in out_dirs:
        process_chunk(out_dir, args.sirius_path, args.port)

    print("\nAll done.")


if __name__ == "__main__":
    main()
