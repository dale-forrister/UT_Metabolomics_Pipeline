# <div align="center"> Overview of Resources </div>

[← Back to Main README](../README.md)


## Table of Contents
  - [Overview of POD Diskspace and Storage](#overview-of-pod-diskspace-and-storage)
  - [Notes on Important Group Folders](notes-on-important-group-folders)

#### Overview of POD Diskspace and storage

We each are given access to three directories:

 - Home Directory - small storage - 100 GB, frequently backed up and only availble to the user.
 - Work Directory - large storage - 16 TB of data that is shared by all users in our group
 - scratch - this is a temporary directory but is a #FAST disk so if you are reading and writing lots of files in your workflow it's useful to first copy your data to scratch and process from there

##### Home directory
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
###### Warning: Watch Your Home Directory Size

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

###### Solution: Move Big Folders to Scratch

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

#### Shared Storage on the Cluster

##### Work vs. Scratch

Each research group has two shared storage spaces:

Work → /stor/work/Sedio/

Backed up weekly and archived to tape roughly once per year.
Best for important research data and results that must be preserved.

##### Our group will maintain - UPLC-MS Files in Work as well as common software we all want to access. i.e. sirius, mzmine and dreaMS

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

#### Moving Files Between Storage Areas

Most users will need to shuffle data between Home, Work, and Scratch.

##### Using mv (simple move)

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

#### Moving Large Files To/From Box with rclone

For very large transfers (e.g., raw data, big outputs), use rclone. This tool syncs files between the cluster and Box (or other cloud storage).

###### 1. Set up rclone with Box

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

###### 2. Copy files to Box
```bash  
rclone copy /stor/work/MyGroup/project1 box:/project1
```
###### 3. Copy files from Box
```bash
rclone copy box:/project1 /stor/work/MyGroup/project1
```
######  4. Sync (mirror) a directory

To make Box and your Work folder match exactly:
```bash
rclone sync /stor/work/MyGroup/project1 box:/project
```

Warning: sync deletes files on the destination if they don’t exist on the source. Use with care!

##### Automating Box Sync with Cron

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

### Notes on Important Group Foldres:
#### a. Conda Envs
#### b. Software

#### Using Conda:
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

```{bash}
/stor/work/sedio/conda_envs
```

Pros: identical, reproducible setups for everyone; large space; backed up.

Cons: only lab maintainers update these (by design).

Plan: You can have your personal envs in Home, but when running specific, standardized parts of the pipeline, activate the shared env.

One-Time Setup (so shared envs show up automatically)

Add the shared env directory to your Conda search path and put Conda’s package cache in Scratch (saves Home quota):

##### Make sure conda is initialized for your shell
conda init bash  # or zsh, etc. Then re-open your shell.

##### Tell conda where to look for environments (adds shared path)
conda config --add envs_dirs /stor/work/sedio/conda_envs

##### (Recommended) Put package caches in Scratch, not Home
conda config --add pkgs_dirs /stor/scratch/sedio/conda_pkgs

##### (Optional) Prefer conda-forge channel and strict priority for reproducibility
conda config --add channels conda-forge
conda config --set channel_priority strict


After this, conda env list will include the shared envs, and you’ll be able to do conda activate <name> if names are unique.

Using the Shared Environments
Activate

You can activate by path (always works):

conda activate /stor/work/sedio/conda_envs/<ENV_NAME>


If you added /stor/work/sedio/conda_envs to envs_dirs, you can also:
```{bash}
conda activate <ENV_NAME>
```
Deactivate
```{bash}
conda deactivate
```
Don’t modify shared envs

Shared envs are read-only for stability. If you need something added:

Ask a maintainer to update the env (see “Maintaining Shared Envs” below), or

Clone it to your Home and modify locally. Note you do not have to clone in order to run common tasks but if you'd like to make changes to the pipeline you can clone it to test out those changes.

```{bash}
conda create -p ~/conda-envs/myproj --clone /stor/work/sedio/conda_envs/<ENV_NAME>
conda activate ~/conda-envs/myproj
mamba install <extra-packages>
```

Creating Your Own Environment (in Home)
##### Faster installs with mamba
```{bash}
mamba create -p ~/conda-envs/myproj python=3.11
conda activate ~/conda-envs/myproj
```

##### Install packages
```{bash}
mamba install numpy pandas jupyterlab
```
##### Save a portable spec for reproducibility (best for Conda)
```{bash}
conda env export --no-builds > ~/myproj_env.yml
```
##### Re-create later (anywhere)
```{bash}
mamba env create -p ~/conda-envs/myproj_recreated -f ~/myproj_env.yml
```

Tip: use -p <path> instead of -n <name> so you control where the env lives and avoid Home clutter. Keep the pkgs cache in Scratch via pkgs_dirs (above) to save Home quota.

Maintaining Shared Environments (for lab maintainers)

Source of truth: an environment.yml (version-controlled in the lab repo).
Deployment path: /stor/work/sedio/conda_envs/<ENV_NAME>

Create or Update a Shared Env
##### Build into the shared path from the YAML
mamba env create -p /stor/work/sedio/conda_envs/<ENV_NAME> -f environment.yml
##### (or update an existing one)
mamba env update  -p /stor/work/sedio/conda_envs/<ENV_NAME> -f environment.yml

Freeze the Environment

For exact reproducibility over time:

##### Export with pinned versions but without build strings (portable)
conda env export --no-builds -p /stor/work/sedio/conda_envs/<ENV_NAME> > environment.lock.yml


Commit environment.yml and environment.lock.yml to the lab repo with a changelog.

Set Permissions (group-read, maintainer-write)
##### Set group ownership once (adjust group name)
chgrp -R sedio /stor/work/sedio/conda_envs

##### Everyone in the group can read/execute, only maintainers can write
chmod -R g+rx,o-rwx /stor/work/sedio/conda_envs
##### For the specific env when deploying:
chmod -R g+rx /stor/work/sedio/conda_envs/<ENV_NAME>


Policy: Users do not install/upgrade packages in shared envs. Changes go through a maintainer PR against environment.yml.

Common Commands Cheat-Sheet
##### List environments (includes shared if envs_dirs is set)
conda env list

##### Activate an env by path (always works)
conda activate /stor/work/sedio/conda_envs/<ENV_NAME>

##### Create a personal env in Home
mamba create -p ~/conda-envs/analysis python=3.11 r-base=4.3

##### Install packages
mamba install -p ~/conda-envs/analysis numpy scipy scikit-learn

##### Export (portable)
conda env export --no-builds -p ~/conda-envs/analysis > ~/analysis_env.yml

##### Recreate from YAML
mamba env create -p ~/conda-envs/analysis2 -f ~/analysis_env.yml

