# <div align="center"> Getting Started: Account, Login & First Connection </div>

[← Back to Main README](../README.md)

This page gets a new lab member from "no account" to "logged in and ready to run the pipeline."
For storage, conda, and `rclone` details see [Overview of Resources](overview_of_resources.md).

---

## 1. Get a POD account

The pipeline runs on the UT Austin **BRCF POD** cluster (Biomedical Research Computing Facility).
Request an account and read the access policy here:

- UT wiki: [POD Resources and Access](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers/pages/31976509/POD+Resources+and+Access)
- Local copy in this repo: [`RCTFusers-POD Resources and Access.pdf`](../RCTFusers-POD%20Resources%20and%20Access-070326-032618.pdf)

Ask a lab admin (Dale) to add you to the **`Sedio`** group so you can read/write `/stor/work/Sedio`.

## 2. Connect to a node

Two ways in:

- **Browser (easiest):** POD OnDemand portal, or one of the login endpoints below.
- **SSH / VS Code Remote-SSH:** connect to a compute node directly (good for running the pipeline).

<details>
<summary>Login endpoints & compute nodes</summary>

Endpoints:
- https://rentcomp01.ccbb.utexas.edu/
- https://rentcomp02.ccbb.utexas.edu/
- https://rentcomp03.ccbb.utexas.edu/

Compute nodes:
- `rentcomp01.ccbb.utexas.edu` — 72 threads, 754 GB RAM
- `rentcomp02.ccbb.utexas.edu` — 72 threads, 251 GB RAM
- `rentcomp03.ccbb.utexas.edu` — 112 threads, 754 GB RAM

</details>

## 3. Know your storage

| Location | Use for |
|---|---|
| `/stor/work/Sedio` | Persistent project data, scripts, results (backed up) |
| `/stor/scratch/Sedio` | Temporary high-speed scratch (not backed up) |
| `~` (home) | Small personal config only; has quota + snapshots |

Raw instrument data and converted `.mzML` stay in their canonical locations — the pipeline
**references** them by path, it does not copy them into project folders.

## 4. Activate the shared toolchain

You do **not** need to install anything — the lab ships ready-made conda environments:

```bash
# general pipeline tools (mzmine helpers, pandas, rclone)
conda activate /stor/work/Sedio/conda_envs/mzmine_processing
```

(SIRIUS fingerprint export uses a second env, `sirius622` — see the SIRIUS docs.)

## 5. Next step

You're ready. Go to **[Part 1: Sample metadata and UPLC run setup](metabolomics_pipeline_part_1.md)**
and follow Parts 1→5 in order, or use the quickstart in the [main README](../README.md).
