# Sedio Lab Group Metabolomics Pipeline
## UT Austin BRCF POD workflow

This repository is the entry point for running the Sedio Lab metabolomics pipeline on the UT POD cluster.

## Start Here
- New users: [Getting Started (account + login + first connection)](docs/getting_started.md)
- Full system/help docs: [Overview of Resources](docs/overview_of_resources.md)
- Pipeline steps: [Main Processing Workflow](#main-processing-workflow)

## Basic POD Usage
1. Connect to a POD node (OnDemand in browser or SSH/VS Code).
2. Work from the correct storage location (`/stor/work/Sedio` for persistent project data, `/stor/scratch/Sedio` for temporary high-speed work).
3. Activate the shared environment for pipeline tools.
4. Run the pipeline in order (convert raw data, process in MZmine, then optional post-processing).

```bash
# Example shared environment activation
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```

## Main Processing Workflow
1. [Part 1: Sample metadata and UPLC run setup](docs/metabolomics_pipeline_part_1.md)
2. [Part 2: Move RAW data and convert with MSConvert](docs/metabolomics_pipeline_part_2.md)
3. [Part 3: Process with MZmine](docs/metabolomics_pipeline_part_3.md)
4. [Part 4: Post-processing with Sirius and dreaMS](docs/metabolomics_pipeline_part_4.md)

## Core Links
- [Getting Started (login/account)](docs/getting_started.md)
- [Overview of POD storage, conda, and rclone](docs/overview_of_resources.md)
- [Practical Computing for Biologists (PDF)](docs/Practical%20Computing%20for%20Biologists.pdf)
- [POD resources and access (UT wiki)](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers/pages/31976509/POD+Resources+and+Access)

<details>
  <summary>Quick Login Endpoints (optional)</summary>

- https://rentcomp01.ccbb.utexas.edu/
- https://rentcomp02.ccbb.utexas.edu/
- https://rentcomp03.ccbb.utexas.edu/

</details>

<details>
  <summary>Compute Nodes</summary>

- `rentcomp01.ccbb.utexas.edu` (CPU: 72 threads, Memory: 754G)
- `rentcomp02.ccbb.utexas.edu` (CPU: 72 threads, Memory: 251G)
- `rentcomp03.ccbb.utexas.edu` (CPU: 112 threads, Memory: 754G)

</details>



