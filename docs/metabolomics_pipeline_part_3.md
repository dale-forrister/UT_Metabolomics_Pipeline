# <div align="center"> Part 3: Processing Raw data with MZmine </div>

[← Back to Main README](../README.md)


## Table of Contents
  - [Overview of POD Diskspace and Storage](#overview-of-pod-diskspace-and-storage)
  - [Notes on Important Group Folders](notes-on-important-group-folders)

## 1. Activate the MZmine environment
MZmine is installed in our shared environment and can be run in headless (batch) mode on the cluster. Follow the steps below to process your datasets.

Before running anything, load the conda environment where MZmine is available:

*** NOTE you have to have configured conda – see [Using Conda](docs/overview_of_resources.md#using-conda)

```{bash}
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```

Now the mzmine command should be available on your PATH. You can check with:

```{bash}
mzmine -h
```

## 2. Generate a project-specific .mzbatch

Use the update script to:

point the batch to your raw files (from metadata),

rewrite all export paths into your --output_dir,

prefix all export filenames with --project_name,

and save the new batch file as <output_dir>/<project_name>.mzbatch.

Required inputs

--mzbatch: Path to the standard/template MZmine batch file (e.g., the lab’s canonical .mzbatch).

--metadata: TSV/CSV containing at least a column of RAW file paths (e.g., mzML_path or FilePath). Optional columns can mark blanks (e.g., Type = Blank).

--output_dir: Where to write all outputs and the new project batch.

--project_name: Prefix used for every exported file name (and the name of the saved .mzbatch).

Example command

```{bash}

python /stor/work/Sedio/software/mzmine/update_mzmine_batch.py \
  --mzbatch /stor/work/Sedio/software/mzmine/Sedio_Lab_mzmine_V4.mzbatch \
  --metadata /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/DemoData_Carya/demo_caryaTRC_metadata.tsv \
  --output_dir /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/Mzmine_outputs/ \
  --project_name Ecomet_Interspecific_Demo

```
What you should see

New batch file: /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/Mzmine_outputs/Ecomet_Interspecific_Demo.mzbatch

All output file entries in the batch rewritten into the same --output_dir, with filenames starting with Ecomet_Interspecific_Demo_…

## 3. Run MZmine (headless) with scratch tmpdir

Set a large heap and a fast local tmp dir (scratch). Ensure the tmp folder exists and is writable.

### create the scratch dir if needed
```{bash}
mkdir -p /ssd1/mzmine_tmp
```

### memory + tmpdir (adjust -Xmx to your node’s RAM)
```{bash}
export JDK_JAVA_OPTIONS="-Xmx400G -Djava.io.tmpdir=/ssd1/mzmine_tmp"
```

### run MZmine headless

```{bash}
/stor/work/Sedio/software/mzmine/bin/mzmine \
  -b /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/Mzmine_outputs/Ecomet_Interspecific_Demo.mzbatch \
  --threads 8 \
  -t /ssd1/mzmine_tmp
```
### remove the temp directory. 

```{bash}
rm -r /ssd1/mzmine_tmp
```
Flags explained

-b: Path to the project batch created in Step 2 (should be <output_dir>/<project_name>.mzbatch).

--threads: Parallel worker threads for MZmine. Tune based on CPU resources.

-t: Scratch/temp directory. Use fast local SSD to speed up I/O.

JDK_JAVA_OPTIONS: Java memory and tmpdir. Set -Xmx at ~70–80% of node RAM to avoid OOM.

## 4. Summary of the output files that are generated
