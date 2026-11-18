# UT Metabolomics Pipeline

**Author: [Dale Forrister](https://dale-forrister.github.io/)** · [website](https://dale-forrister.github.io/) · [GitHub](https://github.com/dale-forrister) —  Stengl-Wyer postdoctoral scholar, Integrative Biology, UT Austin 

This repository is how the **[Sedio Lab](https://briansedio.weebly.com/)**
(UT Austin) processes untargeted LC-MS/MS metabolomics data. You start with a sheet listing your
samples; the pipeline converts the raw instrument files, detects and groups features across all
samples, builds molecular networks, and annotates the features with **SIRIUS** (and, optionally,
**DreaMS** spectral embeddings).

This repo provides detailed documentation for how it can be deployed and used to process metabolomics datasets  processed  in the Sedio_Lab or more generally at UT Austin's Biological Mass Spectrometry Facility.   
The [`docs/`](docs/) walkthroughs provide more details for each step.  

Most steps are run on the Biomedical Research Computing Facilities (BRFC) Rental Pod and an account in the Sedio group is requied. See thier user wiki and [Getting Started](docs/getting_started.md)**,  to learn to connect and create a step.  

### This pipeline is Built on two UT Austin core facilities

- **[Biological Mass Spectrometry Facility](https://research.utexas.edu/cbrs/facilities/)**
  (UT CBRS; RRID:SCR_021728) — samples are run here on a high-resolution **Thermo Orbitrap**
  UPLC-MS/MS. The pipeline is **optimized for Orbitrap data**: high-resolution centroided spectra,
  and SIRIUS runs with its `orbitrap` instrument profile.
- **[Biomedical Research Computing Facility (BRCF)](https://research.utexas.edu/cbrs/facilities/brcf)**
  — all processing runs on its shared "POD" cluster
  ([users wiki](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers)).

## Overview of Pipeline

![UT Metabolomics Pipeline overview](docs/UT_pipeline_overview.png)


## Pipeline Processing steps

The numbered steps match the diagram above.

| # | Step | Tool (version) | Output | Learn more |
|---|---|---|---|---|
| **1** | Submit sample & build the metadata sheet | UT Biological Mass Spec Facility (Thermo Orbitrap) · `check_metadata.py` | validated sample sheet | [Part 1 — Metadata](docs/metabolomics_pipeline_part_1.md) |
| **2** | Convert RAW → mzML | MS_Autoconverter (nightly) or manual CSV · MSConvert / ProteoWizard | MS-only `.mzML` | [ms_auto_converter repo ↗](https://github.com/dale-forrister/ms_auto_converter) |
| **3** | Feature processing | MZmine 4.10.90 (+ Sedio-Lab mzbatch template) | quant table, molecular networks, GNPS & SIRIUS exports | [Part 3 — MZmine](docs/metabolomics_pipeline_part_3.md) |
| **4** | Structural annotation | SIRIUS 6.5.4 (CSI:FingerID, CANOPUS) | formulas, structures, fingerprints, compound classes | [Part 4 — SIRIUS & DreaMS](docs/metabolomics_pipeline_part_4.md) |
| **5** | Ecometabolomic analysis | eCOMET (R package) | diversity & enrichment statistics, plots | [eCOMET package ↗](https://github.com/phytoecia/eCOMET) |

Also in the pipeline: **MS2Deepscore / DreaMS** molecular networking (optional; can run
GPU-accelerated for large datasets — the "AMD Pod" in the diagram), **SIRIUS at scale** (chunked,
resumable; see [Part 5](docs/metabolomics_pipeline_part_5.md)), and **GNPS / FBMN** export. Built with
**rclone**, **Python 3** + pandas — all pre-installed on POD, nothing to install.

## What you provide: the sample sheet

A `.tsv` or `.csv` with **one row per injection**. Required columns (checked by `check_metadata.py`):

| Column | Required? | Meaning |
|---|---|---|
| `Sample_Type` | **yes** | one of `Sample` / `Blank` / `Standard` (≥ 1 `Blank` is needed for blank subtraction) |
| `Full_path` | **yes** | absolute path to the converted `.mzML` for that injection |
| anything else | optional | species, treatment, traits… — carried through into the results |

(If your files aren't listed by full path, `check_metadata.py --resolve-dir <dir>` can locate them by
filename instead.)

## The main pieces

- **MSConvert / ms_auto_converter** — a cron job
  ([ms_auto_converter](https://github.com/dale-forrister/ms_auto_converter)) converts new instrument
  files automatically each night and syncs them to Box. When you need to convert your own data, or
  the auto-converter is down, run it manually from a CSV. Both paths, and the three conversion
  presets, are documented in **[Part 2](docs/metabolomics_pipeline_part_2.md)**.
- **MZmine batch updater** (`update_mzmine_batch.py`) — you don't hand-edit MZmine batch files. The
  updater takes your metadata sheet and fills the sample list, blank-subtraction groups, and output
  names into a **batch template**, producing a run-ready `.mzbatch`.
- **Default batch template** (`resources/mzbatch/`) — a versioned MZmine template whose parameters
  are tuned for the **lab's standard extraction and UPLC-MS protocol** (gradient + Orbitrap
  settings). It is the default, but you can point the updater at an **alternate template**
  (`--mzbatch <your_template>`) for a different method.
- **MS2Deepscore & DreaMS networking** — these run **inside the MZmine batch** as molecular-networking
  steps for normal-sized projects. For very large projects they can be computed **separately on a
  GPU** (they are the memory-heaviest steps) and merged back in.
- **SIRIUS at scale** (`code/sirius_batch_processing/`) — splits the SIRIUS MGF into chunks and runs
  them resumably, for projects too large to do in one pass.

## Quickstart

> Condensed path for someone with a POD account and a sample sheet. Full detail in [`docs/`](docs/).

```bash
PY=/stor/work/Sedio/conda_envs/mzmine_processing/bin/python
MZMINE=/stor/work/Sedio/software/mzmine_41090/bin/mzmine

# 1. Validate the sample sheet (checks Sample_Type, Full_path, blanks, that every file exists)
$PY code/mzmine_processing/check_metadata.py my_samples.tsv

# 2. Build a run-ready MZmine batch from the metadata + the default template
$PY code/mzmine_processing/update_mzmine_batch.py \
    --mzbatch    resources/mzbatch/r12_networking_libV3.mzbatch \
    --metadata   my_samples.tsv \
    --output_dir my_project/mzmine_out \
    --project_name MyProject \
    --path_col   Full_path \
    --library    /path/to/UT_Austin_in_house_V3_mixRT.json      # see resources/libraries/README.md

# 3. Run MZmine (one project at a time — see the warning below)
_JAVA_OPTIONS=-Xmx48G $MZMINE -b my_project/mzmine_out/MyProject.mzbatch -user <you>.mzuser

# 4. SIRIUS on the *_sirius.mgf  (see docs/metabolomics_pipeline_part_5.md)
$PY code/sirius_batch_processing/split_mgf_randomized.py -i my_project/mzmine_out/MyProject_sirius.mgf ...
bash   code/sirius_batch_processing/run_sirius_batches.sh ...
```

> ⚠️ **Run heavy steps one at a time.** MZmine and SIRIUS memory-map large data; several concurrent
> `-Xmx48G` jobs will exhaust the node's memory. Process projects sequentially.

## Documentation

| Guide | Covers |
|---|---|
| [Getting Started](docs/getting_started.md) | account, login, first connection, storage |
| [Part 1 — Metadata & UPLC setup](docs/metabolomics_pipeline_part_1.md) | the sample sheet, run layout |
| [Part 2 — RAW → mzML (MSConvert)](docs/metabolomics_pipeline_part_2.md) | auto-converter, manual CSV, the 3 presets |
| [Part 3 — MZmine processing](docs/metabolomics_pipeline_part_3.md) | feature finding, networking, exports |
| [Part 4 — SIRIUS & DreaMS](docs/metabolomics_pipeline_part_4.md) | structural annotation, embeddings |
| [Part 5 — SIRIUS at scale](docs/metabolomics_pipeline_part_5.md) | chunked, resumable batch runs |
| [Overview of Resources](docs/overview_of_resources.md) | POD storage, conda, rclone, cheat-sheets |

## Repository layout

```
UT_Metabolomics_Pipeline/
├── README.md
├── code/
│   ├── mzmine_processing/         ← check_metadata.py, update_mzmine_batch.py
│   ├── sirius_batch_processing/   ← split → run → merge SIRIUS at scale
│   └── Example_UV_VIS_extraction.R
├── resources/
│   ├── mzbatch/                   ← versioned MZmine batch template(s)
│   └── libraries/                 ← spectral libraries (on POD, not in git — see its README)
└── docs/                          ← the numbered walkthroughs above
```

## Roadmap

Working today (run step-by-step as documented):

- ✔ Conversion — automatic daily converter **and** manual CSV
- ✔ Metadata validation + MZmine batch generation from a sample sheet
- ✔ MZmine feature finding, grouping, and molecular networking (cosine, MS2Deepscore, DreaMS)
- ✔ SIRIUS annotation, including resumable at-scale batch processing
- ✔ DreaMS spectral embeddings

Planned:

- ◻ **Snakemake** wrapper — one command from sample sheet to results, with memory-aware scheduling
- ◻ Small demo dataset + a CI `--dry-run` check
- ◻ Downstream **eCOMET** (R) handoff for statistics, plots, and figures

## Acknowledgments & citation

Developed by **Dale Forrister** (Sedio Lab, UT Austin). This work relies on two UT Austin core
facilities — the **Biological Mass Spectrometry Facility** (RRID:SCR_021728) and the **Biomedical
Research Computing Facility (BRCF)**; please acknowledge them (and the facility RRID) in publications
that use this pipeline. Built on the open-source [MZmine](https://mzio.io/),
[SIRIUS](https://bio.informatik.uni-jena.de/software/sirius/), and
[DreaMS](https://github.com/pluskal-lab/DreaMS) projects — please cite those tools as well.
