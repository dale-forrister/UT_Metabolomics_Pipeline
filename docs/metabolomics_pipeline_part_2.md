# <div align="center"> Part 2: Moving RAW data from the Metabolomics Core and Converting with MSConvert </div>

[← Back to Main README](../README.md)

---

## Table of Contents
- [Configuring `rclone` with UT\_Box (one-time)](#configuring-rclone-with-ut_box-one-time)

- [Downloading from Core and Converting (with or without UV)](#downloading-from-core-and-converting-with-or-without-uv)
  - [1) Activate environment](#1-activate-environment)
  - [2) Prepare the CSV mapping file](#2-prepare-the-csv-mapping-file)
  - [3) Run the converter](#3-run-the-converter)
  - [4) Optional flags](#4-optional-flags)

---


> Each user configures their **own** `rclone` remote. The config is saved at `~/.config/rclone/rclone.conf`.

### Create the remote

# Start interactive setup
*** NOTE you have to have configured conda – see [Using Conda](docs/overview_of_resources.md#using-conda)

```bash
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```
### You will need to make sure rclone is configured and you have access and can view your box files...


This will list all the folders in your base directory of UT_Box:

```bash
rclone lsd UT_Box:
```

This should list all of the folders you have access to...

*** NOTE if rclone is not configured follow these steps - [configure rclone](UT_Metabolomics_Pipeline/docs/overview_of_resources.md#rclone)


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

## Basic mzML Converter - this will remove all UV data to keep the file sizes down in mzMine. 

You have to change the path and name of the csv file.
This will save the files based on the mzML_path column in your csv

```bash
python3 /stor/work/Sedio/software/msconvert/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --scratch-dir /ssd1/temp_msconvert \
  --jobs 4
```

### Note, once you are happy with the conversion please remove the scratch directory that was created...

```bash
rm -rf /ssd1/temp_msconvert/*
```
## Include UV Converter - to keep the uv data in the files add the flagg --include-uv

* For simplicity you can just include this unless you have ALOT of files and are worried mzmine can't handle it. 

```bash
python3 /stor/work/Sedio/software/msconvert/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --include-uv \
  --scratch-dir /ssd1/temp_msconvert \
  --jobs 4
```
### Note, once you are happy with the conversion please remove the scratch directory that was created...

```bash
rm -rf /ssd1/temp_msconvert/*
```

## Optionally you can also have it automatically push the files back up to box if you give it a directory in box you want them copied to. This will create two copies.

python3 /stor/work/Sedio/software/msconvert/msconvert-batch.py \
  --csv /path/to/mapping.csv \
  --include-uv \
  --scratch-dir /ssd1/temp_msconvert \
  --jobs 4 \
  --push-remote UT_Box:2025_Sedio/Processed_Data \
  --rclone-args "--transfers 8 --checkers 16 --progress"

### Note, once you are happy with the conversion please remove the scratch directory that was created...

```bash
rm -rf /ssd1/temp_msconvert/*
```

## For Reference if you are converting off the POD. 
This code using mzmine that has been installed w/ the docker image https://hub.docker.com/r/proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses so that i can be run on linux but contains the vendor specific files. On a windows or on a mac w/ the docker you can convert them samples you self using the following flags...

MS-Only Conversion (No UV)
```bash
msconvert.exe SAMPLE.raw \
  --mzML \
  --filter "peakPicking true 1-" \
  --filter "zeroSamples removeExtra" \
  --64 \
  --zlib \
  --filter "msLevel 1-" \
  -o .
```
 W/ UV 

```bash
msconvert.exe SAMPLE.raw \
  --mzML \
  --filter "peakPicking true 1-" \
  --filter "zeroSamples removeExtra" \
  --64 \
  --zlib \
  --chromatogramFilter "index 0-" \
  -o .

```

If you run on a mac though docker you can run like this...

```bash
docker run --rm \
  -v /path/to/raws:/data \
  proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses \
  wine msconvert.exe /data/SAMPLE.raw \
    --mzML \
    --filter "peakPicking true 1-" \
    --filter "zeroSamples removeExtra" \
    --64 \
    --zlib \
    --chromatogramFilter "index 0-" \
    -o /data
```
