# <div align="center"> Part 2: Moving RAW data from the Metabolomics Core and Converting with MSConvert </div>

[← Back to Main README](../README.md)

---

## Table of Contents
- [Configuring `rclone` with UT\_Box (one-time)](#configuring-rclone-with-ut_box-one-time)
  - [Create the remote](#create-the-remote)
  - [Authorize from a browser](#authorize-from-a-browser)
  - [Verify](#verify)
- [Downloading from Core and Converting (with or without UV)](#downloading-from-core-and-converting-with-or-without-uv)
  - [1) Activate environment](#1-activate-environment)
  - [2) Prepare the CSV mapping file](#2-prepare-the-csv-mapping-file)
  - [3) Run the converter](#3-run-the-converter)
  - [4) Optional flags](#4-optional-flags)

---

## Configuring `rclone` with UT_Box (one-time)

> Each user configures their **own** `rclone` remote. The config is saved at `~/.config/rclone/rclone.conf`.

### Create the remote
```bash
# Check rclone is installed
rclone version
```

# Start interactive setup
```bash
rclone config
```
When prompted:

n (New remote)

Name: UT_Box ← use exactly this so the scripts work

Storage: type box
Client ID/Secret: press Enter to use rclone defaults (or supply your own if you have them)
Edit advanced config? n
Use auto config? If you’re on a headless cluster, answer n (No).
Authorize from a browser
If you answered No to auto config, rclone will print a command to run on a machine with a browser. On your laptop:
rclone authorize "box"
Log in to UT Box in the browser; when it prints a JSON token, copy it back into the cluster prompt where rclone config is waiting.
Finish the wizard by accepting the defaults.

Verify
# You should see a listing (replace the path with something you can access)

```bash
rclone lsd UT_Box:
```

This should list all of the folders you have access to...

## Downloading from Core and Converting (with or without UV)
1) Activate environment
```bash
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```
3) Prepare the CSV mapping file

The CSV must have two columns: raw_input and mzML_path.

raw_input is the source (UT_Box path or a local path)

mzML_path is the destination file path for the output .mzML

Example (mapping.csv):

raw_input,mzML_path
UT_Box:2025_Sedio/Jul/9980/I1_C1_1.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C1_1.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C1_2.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C1_2.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C1_3.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C1_3.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C1_4.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C1_4.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C1_5.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C1_5.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C2_1.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C2_1.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C2_2.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C2_2.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C2_3.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C2_3.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C2_4.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C2_4.mzML
UT_Box:2025_Sedio/Jul/9980/I1_C2_5.raw,/stor/work/Sedio/UPLCMS_Data/Test_UV_Data/I1_C2_5.mzML

3) Run the converter

The script stages all RAWs to the fast scratch area first, then converts.
Adjust the script path below if you keep it somewhere else.

Default (UV/PDA spectra removed; keep basic chromatograms):

```bash
python /stor/work/Sedio/UPLCMS_Data/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --jobs 4
```

Include UV/PDA (process entire file, all chromatograms):

```bash
python /stor/work/Sedio/UPLCMS_Data/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --include-uv \
  --jobs 4
```

4) Optional flags

Force re-download everything from Box/local sources (refresh stage):

```bash
python /stor/work/Sedio/UPLCMS_Data/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --force-download \
  --jobs 4
```

Cleanup staged RAWs from scratch after successful conversion:

```bash
python /stor/work/Sedio/UPLCMS_Data/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --cleanup \
  --jobs 4
```

Notes

Staging directory (default): /stor/work/Sedio/scratch/Temp_Raw_UPLC_Data/

--jobs controls parallel files converted at once (start with 2–4 and adjust).

Flags can be combined as needed (e.g., --include-uv --cleanup --jobs 6).





