# <div align="center"> Part 3: Processing Raw data with MZmine </div>

[← Back to Main README](../README.md)


## Table of Contents
  - [Overview of POD Diskspace and Storage](#overview-of-pod-diskspace-and-storage)
  - [Notes on Important Group Folders](notes-on-important-group-folders)

## 1. Activate the MZmine environment
MZmine is installed in our shared environment and can be run in headless (batch) mode on the cluster. Follow the steps below to process your datasets.

Before running anything, load the conda environment where MZmine is available:

```{bash}
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```

Now the mzmine command should be available on your PATH. You can check with:

```{bash}
mzmine -h
```

## 2. Copy your raw data to scratch

Never run directly from your home or work directory — use scratch for fast I/O. Copy your .mzML files into your scratch user directory:

```{bash}
cp -r /stor/work/Sedio/your_project/data/*.mzML /stor/scratch/$USER/your_project/
```

Make sure all your input .mzML files are inside this scratch directory.

## 3. Edit your batch file

MZmine workflows are defined in XML batch files. You can prepare these locally with the MZmine GUI, then upload them to the cluster.

Open your batch file (workflow.batch.xml) in a text editor.

Update the input file path to point to your scratch directory, for example:

```
<batch>
  <parameter name="Input file" value="/stor/scratch/$USER/your_project/*.mzML"/>
  <!-- additional workflow steps -->
</batch>
```


Set your output path to a directory in scratch as well:

```
<parameter name="Output file" value="/stor/scratch/$USER/your_project/results/output.csv"/>
```

## 4. Run MZmine headless

Once your batch file is configured, launch MZmine in headless mode:

```
mzmine -b /stor/scratch/$USER/your_project/workflow.batch.xml
```

This will process all the .mzML files according to your workflow and write results to the defined output path.

## 5. Collect results

When the run is complete, copy the results back to your work directory for long-term storage:
```
cp -r /stor/scratch/$USER/your_project/results /stor/work/Sedio/your_project/
```
