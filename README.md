#### Sedio Lab Group Metabolomics Pipeline Using the UT Austin Biomedical Research Computing Facility (BRCF) - aka Pods


## Table of Contents
- [Connecting to Pods](#connecting-to-cpu-rental-pods)
  - [Connecting to a Remote Server with VS Code](#1-connecting-to-a-remote-server-with-vs-code)
  - [Connecting to a Remote Server with Ondemand](#2-connecting-to-a-remote-server-through-the-browser-using-ondemand)

# Connecting to CPU Rental Pods:
## 1. Connecting to a Remote Server with VS Code

Visual Studio Code, a powerful and versatile code editor, can be transformed into a robust remote development environment. By connecting to a remote server, you can edit files and run commands as if you were working directly on that machine. This tutorial will guide you through connecting to a server using the popular "Remote - SSH" extension.

### Prerequisites

Before you begin, make sure you have installed Visual Studio Code (VS Code). You can find installation tutorials here:

  * **Windows**: [How to install Visual Studio Code on Windows 10/11](https://www.youtube.com/watch?v=2Gz-uuQWxu4)
  * **macOS**: [How to Install Visual Studio Code on Mac](https://www.youtube.com/watch?v=w0xBQHKjoGo)

It is also recommended that you read the first two parts of ["Practical Computing for Biologists" by Haddock and Dunn](<Practical Computing for Biologists.pdf>) to learn the basics of Linux and the Shell.

### Step 0: Create Your POD Account

1.  Request a POD account [here](https://rctf-account-request.icmb.utexas.edu/). You can also learn more about POD resources [here](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers/pages/31976153/POD+Accounts).

2.  In the "Affiliation" field, select "Sedio_Brian". Please note that it may take 1-2 days for your account to be activated for SSH access to the computing clusters.

3.  We currently have three nodes available on POD (server addresses listed below):

    1.  `rentcomp01.ccbb.utexas.edu` (CPU: 72 threads, Memory: 754G)
    2.  `rentcomp02.ccbb.utexas.edu` (CPU: 72 threads, Memory: 251G)
    3.  `rentcomp03.ccbb.utexas.edu` (CPU: 112 threads, Memory: 754G)

4.  These nodes are shared with other labs, so please be mindful of your resource usage to avoid overloading the system. The POD manager will restrict processes that use excessive resources. You may receive an email notification like this:

    ```
    The process: [PID: 2136120] /stor/home/bf22265/micromamba/envs/dreams/bin/python
    owned by bf22265 (UID: 601015) has been modified:

    This process was reniced for excess CPU time usage
    The current nice value of this process is 19
    This process has consumed 204 minutes of CPU time.
    ```

### Step 1: Install the "Remote - SSH" Extension

1.  Open **VS Code**.
2.  Navigate to the **Extensions** view by clicking the square icon in the sidebar on the left, or by pressing `Ctrl+Shift+X` (Windows) or `Cmd+Shift+X` (macOS).
3.  In the search bar, type `Remote - SSH`.
4.  Locate the extension provided by **Microsoft** and click the **Install** button.

### Step 2: Connect to the Remote Server

Once the extension is installed, a new "Remote Explorer" icon will appear in the activity bar.

1.  Click the new **Remote Explorer** icon in the activity bar.

2.  Ensure that `SSH Targets` is selected from the dropdown menu at the top of the Remote Explorer view.

3.  Click the **+** (**Add New**) icon to add a new SSH connection.

4.  Enter the SSH command to connect to your server in the following format:

    ```bash
    # Your username is often your EID
    ssh your_username@your_server_address

    # Here is an example:
    ssh bf22265@rentcomp01.ccbb.utexas.edu

    # You can change the server address to log in to a different node
    ssh bf22265@rentcomp02.ccbb.utexas.edu
    ```

5.  You will be prompted to select an SSH configuration file. Choose the default location offered, which is typically in the `.ssh` folder within your user's home directory.

### Step 3: Authenticate and Connect

1.  After adding the host, it will appear in your list of SSH Targets in the Remote Explorer.

2.  Hover over the host you just added and click the **Connect to Host in New Window** icon (it looks like a folder with a plus sign).

3.  A new VS Code window will open. If this is your first time connecting, you may be prompted to confirm the server's fingerprint. Type `yes` and press **Enter**.

4.  Next, you will be prompted for your password. Enter your POD account password and press **Enter**.

      * **Note on SSH Keys:** If you have configured an SSH key for your server, you may not be prompted for a password. You can learn more about passwordless access [here](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers/pages/31976509/POD+Resources+and+Access).

5.  Once the connection is successful, you will see your server's address in the green status bar at the bottom-left corner of the VS Code window. This indicates that you are now working on the remote server.

### Step 4: Open a Folder on the Remote Server

Now that you are connected, you can open a project folder from the remote server.

1.  Click **Open Folder** in the Explorer sidebar.
2.  A dialog will appear showing the file system of your remote server.
3.  Navigate to the directory you want to work in, select it, and click **OK**.

The folder's contents will appear in the VS Code Explorer. You can now create, edit, and delete files on your remote server directly from VS Code. The integrated terminal (`Ctrl+Shift+~`) will also now open a terminal session on your remote server.

Congratulations! You have successfully connected to a remote server with VS Code. You can now enjoy a seamless remote development experience with the full power of your favorite editor.

## 2. Connecting to a Remote Server through the browser using ondemand

This is by far the easiest way to connect. It is also the best way to run R on the server. I generally prefer vscode for python rather than Jupyterhub but you can explore both options.

Follow this link depending on which compute node you are are targeting.

 [https://rentcomp1.ccbb.utexas.edu/](https://rentcomp01.ccbb.utexas.edu/)
 
 [https://rentcomp2.ccbb.utexas.edu/](https://rentcomp02.ccbb.utexas.edu/)

 [https://rentcomp3.ccbb.utexas.edu/](https://rentcomp03.ccbb.utexas.edu/)

  You can choose between:
  RStudio
  Jupyterhub

  When you are coding here you will be running on the cluster through web browser


## 2. Overview of Resrouce

### Overview of POD Diskspace and storage

We each are given access to three directories:

 - Home Directory - small storage - 100 GB, frequently backed up and only availble to the user.
 - Work Directory - large storage - 16 TB of data that is shared by all users in our group
 - scratch - this is a temporary directory but is a #FAST disk so if you are reading and writing lots of files in your workflow it's useful to first copy your data to scratch and process from there

#### Home directory
Your Home directory on a POD is located under /stor/home. Home directories are meant for storing small files. All home directories have a 100 GB quota.
Home directory snapshots
Read-only snapshots are periodically taken of your home directory contents. Like Windows backups or Macintosh Time Machine, these backups only consume disk space for files that change (are updated or deleted), in which case the previous file state is "saved" in a snapshot.

Snapshots are stored in a .zfs/snapshot directory under your home directory. To see a list of the snapshots you currently have:

ls ~/.zfs/snapshot
To recover a changed or deleted file, first identify the snapshot it is in, then just copy the file from that snapshot directory to its desired location.

Home directory quotas
Your 100 GB Home directory includes snapshot data. These snapshot backups only consume disk space for files that change (are updated or deleted), in which case the previous file state is "saved" in the snapshot. Snapshots are taken frequently, so their data persists for several months even if the associated Home directory file has been deleted.

The main consequence of this snapshot behavior is that they can cause your 100 GB Home directory quota to be exceeded, even after non-snapshot files have been removed.

While you can view and copy files in your ~/.zfs/snapshot snapshot directories, you cannot write to them or delete them. Please contact us at rctf-support@utexas.edu to remove your snapshots if you exceed your Home directory quota.
##### Warning: Watch Your Home Directory Size

Your Home directory has a strict quota (a size limit). If you exceed it, programs may crash or refuse to start (e.g. RStudio won’t launch).

Hidden sub-directories in your Home—especially those created by RStudio Server, JupyterHub, or Conda—can silently grow very large. Common culprits include:

~/.local/share/rstudio
~/.local/share/jupyter
~/.cache
~/.conda

These folders often contain cached sessions, logs, or temporary files that can balloon into gigabytes.

Run this command to see the size of the usual suspects:

```bash
du -sh ~/.local/share/rstudio ~/.local/share/jupyter ~/.cache ~/.conda 2>/dev/null
```

Example output:

2.5G    /home/username/.local/share/rstudio
500M    /home/username/.local/share/jupyter
1.2G    /home/username/.cache

##### Solution: Move Big Folders to Scratch

If one of these folders is too big, you can move it to your Scratch area (which has much more space) and replace it with a symbolic link. This makes the program think it’s still writing to Home, but the data actually lives in Scratch.

Here’s the process (example shown for RStudio):

Make a new directory in Scratch:
```bash
mkdir -p /stor/scratch/Sedio/<yourusername>/home_extra
```

Copy the heavy folder into Scratch:

```bash
rsync -avrP ~/.local/share/rstudio/ \
    /stor/scratch/Sedio/<yourusername>/home_extralocal_rstudio/
```

Remove the old folder in Home:

```bash
rm -rf ~/.local/share/rstudio
```

Create a symbolic link back to Home:
```bash
ln -sf /stor/scratch/Sedio/<yourusername>/home_extralocal_rstudio/ \
    ~/.local/share/rstudio
```
That’s it — from now on, RStudio will keep writing to Scratch automatically.

### Shared Storage on the Cluster

#### Work vs. Scratch

Each research group has two shared storage spaces:

Work → /stor/work/Sedio/

Backed up weekly and archived to tape roughly once per year.
Best for important research data and results that must be preserved.

#### Our group will maintain - UPLC-MS Files in Work as well as common software we all want to access. i.e. sirius, mzmine and dreaMS

Scratch → /stor/scratch/Sedio/

Also large quota.

Not backed up — files can be deleted without notice.

Best for temporary or reproducible data (e.g., downloads, intermediate results).

To check which groups you belong to:

```bash
groups
```
Both areas are shared by everyone in your group, and you can create whatever directory structure makes sense (user folders are not auto-created).

Backups and Archiving

Home and Work directories are backed up weekly (Friday–Monday).

Scratch is never backed up.

Directories named tmp, temp, or backups are excluded from backups.

Backups are occasionally archived to TACC’s Ranch tape archive (roughly once a year).

Old project data may be moved into “long term archives (LTA)” or off the cluster entirely to save space.

If you need something from tape, you’ll need to contact system admins.

### Moving Files Between Storage Areas

Most users will need to shuffle data between Home, Work, and Scratch.

#### Using mv (simple move)

Quickly move files if staying within the same filesystem:

```bash
mv ~/myproject/data.csv /stor/work/Sedio/<My_Specific_User_Folder>/myproject/

```

Using rsync (safe copy)

rsync is preferred when copying because it preserves file permissions and can resume if interrupted.

Example:

```bash
rsync -avrP ~/myproject/ /stor/scratch/Sedio/<My_Specific_User_Folder>/myproject_test/
```

What the flags mean:

-a → archive mode (preserves permissions, symlinks, timestamps, etc.)

-v → verbose (shows what’s happening)

-r → recursive (copies subdirectories)

-P → progress + partial (shows progress and allows resume if interrupted)

Copy example
```bash
rsync -avrP /stor/work/Sedio/<My_Specific_User_Folder>/project1/ /stor/scratch/Sedio/<My_Specific_User_Folder>/project1_copy/
```

This makes a full copy of project1 from Work into Scratch.

### Moving Large Files To/From Box with rclone

For very large transfers (e.g., raw data, big outputs), use rclone. This tool syncs files between the cluster and Box (or other cloud storage).

##### 1. Set up rclone with Box

Run:
```bash
rclone config
```

Follow prompts:

Choose n for a new remote.

Give it a name (e.g., box).

Select Box from the provider list.

Accept defaults unless you need advanced options.

rclone will open a browser window for you to log into Box and grant access.

Once complete, you’ll have a working Box remote (called box in this example).

##### 2. Copy files to Box
```bash  
rclone copy /stor/work/MyGroup/project1 box:/project1
```
##### 3. Copy files from Box
```bash
rclone copy box:/project1 /stor/work/MyGroup/project1
```
#####  4. Sync (mirror) a directory

To make Box and your Work folder match exactly:
```bash
rclone sync /stor/work/MyGroup/project1 box:/project
```

Warning: sync deletes files on the destination if they don’t exist on the source. Use with care!

#### Automating Box Sync with Cron

If you regularly move files between the cluster and Box, you can schedule it with a cron job (automated task runner on Linux).

1. Open the crontab editor
```bash
crontab -e
```
3. Add a sync job

For example, to sync your Work project to Box every night at 2 AM:
```bash
0 2 * * * rclone sync /stor/work/MyGroup/project1 box:/project1 >> ~/rclone_project1.log 2>&1
```

Explanation:
0 2 * * * → runs at 02:00 every day.
rclone sync ... → command to run.
>> ~/rclone_project1.log 2>&1 → saves logs so you can check if it worked.

3. Check your jobs
```bash
crontab -l
```

## 3. Notes on Important Group Foldres:
### a. Software
### b. Conda Envs

### Using Conda:
Conda Environments for the Lab
What is Conda (and why we use it)

Conda is a package and environment manager. It lets you:

install software (R/Python + libraries, CLI tools) without admin rights,

keep multiple, isolated environments (different versions for different projects),

make work reproducible by saving and restoring environment definitions.

We strongly recommend using mamba (a drop-in faster Conda replacement) for speed. You can still activate environments with conda activate … even if you install them with mamba.

Lab Policy: Per-User vs Shared Environments
Per-User (in Home)

Each user can create their own environments in Home for personal work.

Pros: freedom to experiment.

Cons: can eat Home quota if you’re not careful.

Shared (group-maintained)

The lab maintains read-only, group environments for critical pipelines under:

/stor/work/sedio/conda_envs


Pros: identical, reproducible setups for everyone; large space; backed up.

Cons: only lab maintainers update these (by design).

Plan: You can have your personal envs in Home, but when running specific, standardized parts of the pipeline, activate the shared env.

One-Time Setup (so shared envs show up automatically)

Add the shared env directory to your Conda search path and put Conda’s package cache in Scratch (saves Home quota):

# Make sure conda is initialized for your shell
conda init bash  # or zsh, etc. Then re-open your shell.

# Tell conda where to look for environments (adds shared path)
conda config --add envs_dirs /stor/work/sedio/conda_envs

# (Recommended) Put package caches in Scratch, not Home
conda config --add pkgs_dirs /stor/scratch/sedio/conda_pkgs

# (Optional) Prefer conda-forge channel and strict priority for reproducibility
conda config --add channels conda-forge
conda config --set channel_priority strict


After this, conda env list will include the shared envs, and you’ll be able to do conda activate <name> if names are unique.

Using the Shared Environments
Activate

You can activate by path (always works):

conda activate /stor/work/sedio/conda_envs/<ENV_NAME>


If you added /stor/work/sedio/conda_envs to envs_dirs, you can also:

conda activate <ENV_NAME>

Deactivate
conda deactivate

Don’t modify shared envs

Shared envs are read-only for stability. If you need something added:

Ask a maintainer to update the env (see “Maintaining Shared Envs” below), or

Clone it to your Home and modify locally:

conda create -p ~/conda-envs/myproj --clone /stor/work/sedio/conda_envs/<ENV_NAME>
conda activate ~/conda-envs/myproj
mamba install <extra-packages>

Creating Your Own Environment (in Home)
# Faster installs with mamba
mamba create -p ~/conda-envs/myproj python=3.11
conda activate ~/conda-envs/myproj

# Install packages
mamba install numpy pandas jupyterlab

# Save a portable spec for reproducibility (best for Conda)
conda env export --no-builds > ~/myproj_env.yml

# Re-create later (anywhere)
mamba env create -p ~/conda-envs/myproj_recreated -f ~/myproj_env.yml


Tip: use -p <path> instead of -n <name> so you control where the env lives and avoid Home clutter. Keep the pkgs cache in Scratch via pkgs_dirs (above) to save Home quota.

Maintaining Shared Environments (for lab maintainers)

Source of truth: an environment.yml (version-controlled in the lab repo).
Deployment path: /stor/work/sedio/conda_envs/<ENV_NAME>

Create or Update a Shared Env
# Build into the shared path from the YAML
mamba env create -p /stor/work/sedio/conda_envs/<ENV_NAME> -f environment.yml
# (or update an existing one)
mamba env update  -p /stor/work/sedio/conda_envs/<ENV_NAME> -f environment.yml

Freeze the Environment

For exact reproducibility over time:

# Export with pinned versions but without build strings (portable)
conda env export --no-builds -p /stor/work/sedio/conda_envs/<ENV_NAME> > environment.lock.yml


Commit environment.yml and environment.lock.yml to the lab repo with a changelog.

Set Permissions (group-read, maintainer-write)
# Set group ownership once (adjust group name)
chgrp -R sedio /stor/work/sedio/conda_envs

# Everyone in the group can read/execute, only maintainers can write
chmod -R g+rx,o-rwx /stor/work/sedio/conda_envs
# For the specific env when deploying:
chmod -R g+rx /stor/work/sedio/conda_envs/<ENV_NAME>


Policy: Users do not install/upgrade packages in shared envs. Changes go through a maintainer PR against environment.yml.

CUDA/ROCm & Platform Notes (quick realities)

GPU stacks (PyTorch, JAX, TensorFlow) are hardware-specific. Always match the CUDA/ROCm build to the pod’s drivers.

If we publish a shared GPU env (<ENV_NAME>-gpu), use that exact env for GPU work instead of mixing and matching.

If something fails to import, check python -c "import torch; print(torch.__version__)" and compare to the env’s README.

Common Commands Cheat-Sheet
# List environments (includes shared if envs_dirs is set)
conda env list

# Activate an env by path (always works)
conda activate /stor/work/sedio/conda_envs/<ENV_NAME>

# Create a personal env in Home
mamba create -p ~/conda-envs/analysis python=3.11 r-base=4.3

# Install packages
mamba install -p ~/conda-envs/analysis numpy scipy scikit-learn

# Export (portable)
conda env export --no-builds -p ~/conda-envs/analysis > ~/analysis_env.yml

# Recreate from YAML
mamba env create -p ~/conda-envs/analysis2 -f ~/analysis_env.yml

Space & Quotas: Keep Home Light

Envs in Home count against your Home quota.

Reduce Home usage by setting the package cache to Scratch:

conda config --add pkgs_dirs /stor/scratch/sedio/conda_pkgs


If an env gets huge, consider moving it to Work (for group use) or cloning into Scratch if it’s temporary.

Troubleshooting

CommandNotFoundError: conda
Run conda init bash (or your shell), then open a new terminal.

Environment not found when using name
Use the path: conda activate /stor/work/sedio/conda_envs/<ENV_NAME>
or add envs_dirs (see “One-Time Setup”).

Permission denied when installing in shared env
That’s by design. Clone it to Home or submit a change request to maintainers.

Solver is slow
Use mamba (mamba install …) instead of conda install ….

Example: End-to-End Workflow

Add shared envs and caches:

conda init bash
conda config --add envs_dirs /stor/work/sedio/conda_envs
conda config --add pkgs_dirs /stor/scratch/sedio/conda_pkgs
conda config --add channels conda-forge
conda config --set channel_priority strict


Use a shared pipeline env:

conda activate /stor/work/sedio/conda_envs/metabolomics-pipeline
python run_pipeline.py --config configs/run1.yaml


Customize for a side project (in Home):

conda create -p ~/conda-envs/met-pipe-dev --clone /stor/work/sedio/conda_envs/metabolomics-pipeline
conda activate ~/conda-envs/met-pipe-dev
mamba install seaborn==0.13.2


  
## 4. Instructions to specifc parts of the metabolomics pipeline

### Part 1: Sample Metadata and Setting up a UPLC Run:

### Part 2: Moving Raw data files from the Metabolomics Core and Converting with MSConvert
#Converting raw files

### Part 3: Processing Raw data with MZmine

### Part 4: Post Processing W/ Sirius and Dreams:
#### 4.a Sirius
#### 4.b dreaMS 

