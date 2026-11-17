#!/usr/bin/env python3
import os
import argparse
import random
from math import ceil
from typing import Dict, List, Optional, Tuple

def split_mgf_by_feature(
    input_path: str,
    out_dir: str,
    max_features: int,
    out_prefix: str = "split",
    drop_charge2: bool = False,
    shuffle: bool = True,
    seed: Optional[int] = None,
    round_robin: bool = False,
) -> Tuple[int, int, List[str], dict]:
    """
    Read an MGF, group blocks by FEATURE_ID, optionally drop CHARGE=2* blocks,
    then shuffle FEATURE_ID groups and write them into batch files.

    Returns:
        total_features_after, num_chunks, out_files, stats
    """
    os.makedirs(out_dir, exist_ok=True)

    # Parsing structures
    blocks_by_feature: Dict[str, List[List[str]]] = {}
    seen_features = set()
    feat_has_non_ch2: Dict[str, bool] = {}
    blocks_skipped_ch2 = 0

    # State for current block
    current_block_lines: List[str] = []
    current_feature_id: Optional[str] = None
    current_charge: Optional[str] = None

    def _finish_block():
        nonlocal current_block_lines, current_feature_id, current_charge, blocks_skipped_ch2
        if not current_block_lines:
            return
        if current_feature_id is None:
            # No FEATURE_ID -> drop silently
            current_block_lines = []
            current_charge = None
            return

        seen_features.add(current_feature_id)
        feat_has_non_ch2.setdefault(current_feature_id, False)

        # Drop charge=2* blocks if requested
        if drop_charge2 and current_charge and str(current_charge).strip().startswith("2"):
            blocks_skipped_ch2 += 1
            # Do not store this block
            current_block_lines = []
            current_feature_id = None
            current_charge = None
            return

        # Keep block
        feat_has_non_ch2[current_feature_id] = True
        blocks_by_feature.setdefault(current_feature_id, []).append(current_block_lines)

        # reset
        current_block_lines = []
        current_feature_id = None
        current_charge = None

    # --- Parse MGF ---
    with open(input_path, "r") as f:
        for raw in f:
            line = raw.rstrip("\n")
            U = line.strip().upper()
            if U.startswith("BEGIN IONS"):
                _finish_block()
                current_block_lines = [line + "\n"]
                current_feature_id = None
                current_charge = None
            elif U.startswith("END IONS"):
                current_block_lines.append(line + "\n")
                _finish_block()
            else:
                # Header key=val?
                if "=" in line:
                    key, val = line.split("=", 1)
                    K = key.strip().upper()
                    if K == "FEATURE_ID":
                        current_feature_id = val.strip()
                    elif K == "CHARGE":
                        current_charge = val.strip()
                current_block_lines.append(line + "\n")
        _finish_block()

    total_features_detected = len(seen_features)

    # Features with only CHARGE=2* blocks (removed) when drop_charge2=True
    features_removed_charge2_only = 0
    if drop_charge2:
        for feat in seen_features:
            # If we never stored any non-2+ block for this feature, it was removed
            if not feat_has_non_ch2.get(feat, False):
                features_removed_charge2_only += 1
        # Ensure such features are not present in blocks_by_feature
        # (They won't be, because we only populated blocks when keeping at least one block)
        # But in case of any residue, prune:
        for feat in list(blocks_by_feature.keys()):
            if not blocks_by_feature[feat]:  # empty list
                del blocks_by_feature[feat]

    # --- Shuffle FEATURES ---
    features: List[str] = list(blocks_by_feature.keys())

    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(features)

    # --- Plan batches ---
    if not features:
        out_files: List[str] = []
        stats = {
            "features_detected": total_features_detected,
            "features_removed_charge2_only": features_removed_charge2_only,
            "blocks_skipped_charge2": blocks_skipped_ch2,
            "features_after_filter": 0,
            "batches": 0,
        }
        return 0, 0, out_files, stats

    num_chunks = ceil(len(features) / max_features)

    # Prepare outputs
    out_files: List[str] = []
    out_handles: List[Optional[open]] = []

    def _ensure_handle(idx: int):
        while len(out_handles) <= idx:
            file_idx = len(out_handles) + 1
            ofn = os.path.join(out_dir, f"{out_prefix}_{file_idx:04d}.mgf")
            out_files.append(ofn)
            out_handles.append(open(ofn, "w"))

    # Assign features to chunks
    if round_robin:
        # Spread features across batches evenly (after shuffling)
        for i, feat in enumerate(features):
            chunk_idx = i % num_chunks
            _ensure_handle(chunk_idx)
            h = out_handles[chunk_idx]
            for block_lines in blocks_by_feature[feat]:
                h.writelines(block_lines)
                if not block_lines[-1].endswith("\n"):
                    h.write("\n")
            h.write("\n")
    else:
        # Fill batches sequentially up to max_features, but with shuffled feature order
        for i, feat in enumerate(features):
            chunk_idx = i // max_features
            _ensure_handle(chunk_idx)
            h = out_handles[chunk_idx]
            for block_lines in blocks_by_feature[feat]:
                h.writelines(block_lines)
                if not block_lines[-1].endswith("\n"):
                    h.write("\n")
            h.write("\n")

    for h in out_handles:
        if h:
            h.close()

    total_features_after = len(features)
    stats = {
        "features_detected": total_features_detected,
        "features_removed_charge2_only": features_removed_charge2_only,
        "blocks_skipped_charge2": blocks_skipped_ch2,
        "features_after_filter": total_features_after,
        "batches": num_chunks,
        "assignment": "round_robin" if round_robin else "sequential_after_shuffle",
        "seed": seed if shuffle else None,
    }
    return total_features_after, num_chunks, out_files, stats


def main():
    ap = argparse.ArgumentParser(
        description="Split an MGF by FEATURE_ID, optionally drop CHARGE=2* blocks, and (by default) shuffle features before batching."
    )
    ap.add_argument("-i", "--input", required=True, help="Input MGF")
    ap.add_argument("-o", "--out-dir", required=True, help="Output directory for split MGFs")
    ap.add_argument("--max-features", type=int, required=True, help="Max features per split MGF")
    ap.add_argument("--prefix", default="split", help="Output filename prefix (default: split)")
    ap.add_argument("--drop-charge2", action="store_true", help="Skip any block with CHARGE starting with '2'")
    ap.add_argument("--no-shuffle", action="store_true", help="Disable shuffling of FEATURE_ID groups")
    ap.add_argument("--seed", type=int, default=None, help="Random seed for shuffling (default: None)")
    ap.add_argument("--round-robin", action="store_true", help="Distribute features round-robin across batches after shuffling")

    args = ap.parse_args()

    total_after, num_chunks, out_files, stats = split_mgf_by_feature(
        input_path=args.input,
        out_dir=args.out_dir,
        max_features=args.max_features,
        out_prefix=args.prefix,
        drop_charge2=args.drop_charge2,
        shuffle=not args.no_shuffle,
        seed=args.seed,
        round_robin=args.round_robin,
    )

    print(f"Detected {stats['features_detected']} unique features.")
    if args.drop_charge2:
        print(f"Removed {stats['features_removed_charge2_only']} multi_charged_features (features with only CHARGE=2 blocks).")
        print(f"Dropped {stats['blocks_skipped_charge2']} individual blocks due to CHARGE=2*.")
    print(f"Batches: {stats['batches']}  |  Assignment: {stats['assignment']}  |  Seed: {stats['seed']}")
    print(f"Features after filtering: {stats['features_after_filter']}")
    print("Output MGF files:")
    for p in out_files:
        print(p)


if __name__ == "__main__":
    main()
