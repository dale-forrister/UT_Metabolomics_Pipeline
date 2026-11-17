# <div align="center"> Part 2: Moving RAW Data and Converting with MSConvert </div>

[← Back to Main README](../README.md)

---

Instrument `.raw` files live in **UT_Box**. Before MZmine can use them they must be converted to
open formats (`.mzML` / `.mzXML`) with **MSConvert** (ProteoWizard). There are two ways to do this:

- **[A) Automatic daily converter](#a-automatic-daily-converter-ms_auto_converter)** — a cron job
  converts anything new and syncs it back to Box. Most data is handled this way with no action from you.
- **[B) Manual conversion from a CSV](#b-manual-conversion-from-a-csv)** — run it yourself when the
  auto-converter isn't working, or for one-off / test datasets.

Both call the **same MSConvert engine** through the ProteoWizard Docker image
`proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses` (it bundles the Windows vendor
libraries and runs on Linux via Wine), and both expose the **[same three data-type presets](#the-three-data-type-presets)**.

## Table of Contents
- [Prerequisite: `rclone` + UT_Box](#prerequisite-rclone--ut_box)
- [A) Automatic daily converter (ms_auto_converter)](#a-automatic-daily-converter-ms_auto_converter)
- [The three data-type presets](#the-three-data-type-presets)
- [B) Manual conversion from a CSV](#b-manual-conversion-from-a-csv)
- [Reference: equivalent raw `msconvert` commands](#reference-equivalent-raw-msconvert-commands)

---

## Prerequisite: `rclone` + UT_Box

Each user configures their **own** `rclone` remote named `UT_Box:` (config saved at
`~/.config/rclone/rclone.conf`). Full setup:
[Configuring rclone with UT_Box](overview_of_resources.md#configuring-rclone-with-ut_box-one-time).

```bash
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
rclone lsd UT_Box:      # should list the Box folders you can see
```

---

## A) Automatic daily converter (ms_auto_converter)

Most conversion is automated by a separate repo,
**[ms_auto_converter](https://github.com/dale-forrister/ms_auto_converter)**, deployed on POD at
`/stor/work/Sedio/github_repos/ms_auto_converter`. A **cron job runs it once per day** and you
normally don't touch it — new instrument files just appear, converted, in Box.

**How it works** — the daily entrypoint `code/run_msconvert_daily.sh` runs this chain:

```text
cron
└── run_msconvert_daily.sh
    ├── Check_Raw_Update_Gsheet.py      # refresh the inventory of RAW files…
    │   └── List_Raw_UT_Box.sh          #   …by listing *.raw across the UT_Box year folders
    ├── msconvert-batch_gsheet.py       # convert everything "checked" & not already in Box
    │   └── List_Converted_UT_Box.sh    #   …skips files already converted on Box
    └── rclone sync  →  UT_Box:Converted_UPLCMS_Data/   + scratch cleanup
```

1. **Inventory:** lists every `.raw` in the UT_Box year folders and writes them into a **Google
   Sheet** (tab `Raw_Samples_All`).
2. **Convert:** `msconvert-batch_gsheet.py` reads the sheet, **skips files already on Box**, stages
   the remaining RAWs to SSD scratch (`/ssd1/temp_msconvert`), and runs MSConvert in parallel
   Docker containers, **grouped by data type**.
3. **Which preset each file gets** is driven by the sheet's **`Converted_File_Type`** column
   (`--file-type-col`), one of the three presets below.
4. **Publish:** converted files are written to `/stor/work/Sedio/Converted_UPLCMS_Data`, synced to
   `UT_Box:Converted_UPLCMS_Data/`, and scratch is cleared. Logs land in `converter_logs/`.

> If the auto-converter is stuck (cron not firing, a batch erroring, or you need files *now*), fall
> back to the manual CSV path in **[section B](#b-manual-conversion-from-a-csv)**.

---

## The three data-type presets

Both the automatic and manual converters expose the same three presets. Each is just a shorthand
for a specific set of `msconvert` flags. **Every preset** always applies these base flags:

| Base flag | What it does |
|---|---|
| `--mzML` *or* `--mzXML` | output format |
| `--filter "peakPicking true 1-"` | centroid (peak-pick) all MS levels ≥ 1 |
| `--filter "zeroSamples removeExtra"` | drop padding zero-intensity samples (smaller files) |
| `--64` | 64-bit binary encoding |
| `--zlib` | zlib-compress the binary arrays |

On top of the base, the UV handling differs:

| Preset | Format | UV/PDA kept? | Preset-specific flags added |
|---|---|---|---|
| **`mzML_w_UV`** *(default)* | `.mzML` | only if you also pass `--include-uv` | **with** `--include-uv`: `--chromatogramFilter "index 0-"` (keep *all* chromatograms) · **without**: same MS-only flags as below |
| **`mzML_no_UV`** | `.mzML` | never | `--filter "msLevel 1-"` + `--chromatogramFilter "index 0-2"` |
| **`mzXML`** | `.mzXML` | never | `--filter "msLevel 1-"` + `--chromatogramFilter "index 0-2"` |

What the UV-related flags mean:

- `--filter "msLevel 1-"` — keep only MS scans (level 1+), which **drops the UV/PDA spectra**.
- `--chromatogramFilter "index 0-2"` — keep only the first ~3 chromatograms (TIC/BPC), dropping the
  many UV/PDA chromatograms.
- `--chromatogramFilter "index 0-"` — keep **all** chromatograms (used only when UV is included).

> **Why drop UV?** UV/PDA scans are ~90% of a raw file's "spectra" and MZmine memory-maps all of
> them even though feature finding uses only MS scans. For large projects, UV bloat can blow memory —
> so `mzML_no_UV` (or `mzXML`) is the default for anything scaled up. Keep UV (`mzML_w_UV` +
> `--include-uv`) only when you specifically need the UV trace. See
> [Part 3](metabolomics_pipeline_part_3.md) for the memory implications in MZmine.

---

## B) Manual conversion from a CSV

Use this when the auto-converter isn't running, or for test/one-off data. The canonical script is
in the converter repo:

```
/stor/work/Sedio/github_repos/ms_auto_converter/code/msconvert-batch.py
```

### 1. Activate the environment

```bash
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```

### 2. Prepare the CSV

Two columns — **`raw_input`** and **`output_path`** (header names must match exactly):

- `raw_input` — the source: a `UT_Box:` path **or** a local path to the `.raw`.
- `output_path` — the destination path for the converted file.

```csv
raw_input,output_path
UT_Box:2025_Sedio/Jul/9980/I1_C1_1.raw,/stor/work/Sedio/UPLCMS_Data/Test_Data/I1_C1_1.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C1_2.raw,/stor/work/Sedio/UPLCMS_Data/Test_Data/I1_C1_2.mzML
```

### 3. Run it — pick a preset with `--convert-file-type`

```bash
PY=/stor/work/Sedio/conda_envs/mzmine_processing/bin/python
MSCONV=/stor/work/Sedio/github_repos/ms_auto_converter/code/msconvert-batch.py

# MS-only mzML (recommended default for anything scaled up)
$PY $MSCONV --csv mapping.csv --convert-file-type mzML_no_UV \
    --scratch-dir /ssd1/temp_msconvert --jobs 4

# mzML that keeps UV/PDA (needs BOTH the preset and --include-uv)
$PY $MSCONV --csv mapping.csv --convert-file-type mzML_w_UV --include-uv \
    --scratch-dir /ssd1/temp_msconvert --jobs 4

# mzXML, MS-only
$PY $MSCONV --csv mapping.csv --convert-file-type mzXML \
    --scratch-dir /ssd1/temp_msconvert --jobs 4
```

Useful flags: `--jobs N` (parallel containers), `--dry-run` (print commands only), `--verbose`
(show detected CSV headers), `--cleanup` (delete staged RAW after success), and
`--push-remote REMOTE:PATH` (also upload the results to Box — makes a second copy).

### 4. Clean up scratch when you're happy with the output

```bash
rm -rf /ssd1/temp_msconvert/*
```

---

## Reference: equivalent raw `msconvert` commands

If you're converting **off POD** (Windows/Mac with the ProteoWizard Docker image), these are the
exact commands each preset expands to — the same thing the batch scripts run per file.

**MS-only** (`mzML_no_UV`; use `--mzXML` instead of `--mzML` for the `mzXML` preset):

```bash
docker run --rm -v /path/to/raws:/data \
  proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses \
  wine msconvert.exe /data/SAMPLE.raw \
    --mzML \
    --filter "peakPicking true 1-" \
    --filter "zeroSamples removeExtra" \
    --64 --zlib \
    --filter "msLevel 1-" \
    --chromatogramFilter "index 0-2" \
    -o /data
```

**With UV/PDA kept** (`mzML_w_UV` + `--include-uv`):

```bash
docker run --rm -v /path/to/raws:/data \
  proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses \
  wine msconvert.exe /data/SAMPLE.raw \
    --mzML \
    --filter "peakPicking true 1-" \
    --filter "zeroSamples removeExtra" \
    --64 --zlib \
    --chromatogramFilter "index 0-" \
    -o /data
```

Next: [Part 3 — Processing with MZmine](metabolomics_pipeline_part_3.md).
