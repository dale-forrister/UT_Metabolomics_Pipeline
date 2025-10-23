# <div align="center"> Overview of Resources </div>

[← Back to Main README](../README.md)


## Table of Contents
  - [Overview of POD Diskspace and Storage](#overview-of-pod-diskspace-and-storage)
    - [Home directory](#home-directory)  
    - [Shared Storage on the Cluster](#shared-storage-on-the-cluster)
  - [Moving Files Between Storage Spaces and On and Off Custer](#moving-files)  
  - [Read Only Metabolomics Pipeline Folders](#read-only-metabolomics-pipeline-folders)
    - [Using Conda](#using-conda)
    - [software](#software)
    - [github_repos](#github-repos)
    - [setting up rclone] (#rclone)

## Overview of POD Diskspace and storage

We each are given access to three directories:

 - Home Directory - small storage - 100 GB, frequently backed up and only availble to the user.
 - Work Directory - large storage - 16 TB of data that is shared by all users in our group
 - scratch - this is a temporary directory but is a #FAST disk so if you are reading and writing lots of files in your workflow it's useful to first copy your data to scratch and process from there

### Home directory

Your Home directory on a POD is located under /stor/home. Home directories are meant for storing small files. All home directories have a 100 GB quota.

### Home directory snapshots

Read-only snapshots are periodically taken of your home directory contents. Like Windows backups or Macintosh Time Machine, these backups only consume disk space for files that change (are updated or deleted), in which case the previous file state is "saved" in a snapshot.

Snapshots are stored in a .zfs/snapshot directory under your home directory. To see a list of the snapshots you currently have:

```{bash}
ls ~/.zfs/snapshot
```

To recover a changed or deleted file, first identify the snapshot it is in, then just copy the file from that snapshot directory to its desired location.

#### Home directory quotas
Your 100 GB Home directory includes snapshot data. These snapshot backups only consume disk space for files that change (are updated or deleted), in which case the previous file state is "saved" in the snapshot. Snapshots are taken frequently, so their data persists for several months even if the associated Home directory file has been deleted.

The main consequence of this snapshot behavior is that they can cause your 100 GB Home directory quota to be exceeded, even after non-snapshot files have been removed.

While you can view and copy files in your ~/.zfs/snapshot snapshot directories, you cannot write to them or delete them. Please contact us at rctf-support@utexas.edu to remove your snapshots if you exceed your Home directory quota.

##### Warning: Watch Your Home Directory Size

Your Home directory has a strict quota (a size limit). If you exceed it, programs may crash or refuse to start (e.g. RStudio won’t launch).

Hidden sub-directories in your Home—especially those created by RStudio Server, JupyterHub, or Conda—can silently grow very large. Common culprits include:

```
~/.local/share/rstudio
~/.local/share/jupyter
~/.cache
~/.conda
```

These folders often contain cached sessions, logs, or temporary files that can balloon into gigabytes.

Run this command to see the size of the usual suspects:

```{bash}
du -sh ~/.local/share/rstudio ~/.local/share/jupyter ~/.cache ~/.conda 2>/dev/null
```

Example output:
```
2.5G    /home/username/.local/share/rstudio
500M    /home/username/.local/share/jupyter
1.2G    /home/username/.cache
```
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

### Shared Storage on the Cluster

### Work vs. Scratch

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

## Moving Files

### Moving Files Between Storage Areas

Most users will need to shuffle data between Home, Work, and Scratch.

#### Using mv (simple move)

Quickly move files if staying within the same filesystem:

```bash
mv ~/myproject/data.csv /stor/work/Sedio/<My_Specific_User_Folder>/myproject/

```

#### Using rsync (safe copy)

rsync is preferred when copying because it preserves file permissions and can resume if interrupted.

##### Copy files from source to destination:

rsync -avrP ~/myproject/ /stor/scratch/Sedio/<My_Specific_User_Folder>/myproject_test/

```
-a → archive mode (preserves permissions, symlinks, timestamps, etc.)
-v → verbose
-r → recursive (included in -a, so technically redundant)
-P → shows progress, keeps partial files
```
This copies everything in ~/myproject/ into the destination, overwriting files if the source has changed.
⚠️ Important:

Without --delete, the destination may accumulate old files no longer present in the source.

Sync folders making source match destination exactly

```bash
rsync -avrP --delete ~/myproject/ /stor/scratch/Sedio/<user>/myproject_test/
```
With --delete, the all files that are not in source, but in destination will be removed. Meaning that source and destination will match exactly


### Moving Large Files To/From Box with rclone

For very large transfers (e.g., raw data, big outputs), use rclone. This tool syncs files between the cluster and Box (or other cloud storage).

rclone

#### 1. Set up rclone with Box
## Configuring `rclone` with UT_Box (one-time)
Run:

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

If you answered No to auto config, rclone will print a command to run on a machine with a browser. On your laptop: rclone authorize "box"

Log in to UT Box in the browser; when it prints a JSON token, copy it back into the cluster prompt where rclone config is waiting.

Finish the wizard by accepting the defaults.

Verify you can access and view your box files..
This will list all the folders in your base directory of UT_Box:

```bash
rclone lsd UT_Box:
```

This should list all of the folders you have access to...


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

### Automating Box Sync with Cron

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

## Read Only Metabolomics Pipeline Folders:

DLF has created key folders within the main directory of the /stor/work/Sedio/ some of which are read only so that we can maintain the working metabolomics pipelines in a shared space. The key folders are:

Read Only:
- conda_envs
- software
- github_repos

Read and Write by all users:
- scratch - this is a sym link the main scratch space everything in here should be considered temporary and might get deleted periodically.
  - scratch/user_directories - each user in our group gets there own scratch folder to store there own temporary files without the file storage limit. This is a fast drive so it can help to first copy here for some tasks
- UPLCMS_Data - this will store UPLCMS_Data in raw format and have folders for converted mzML files for each project.
- user_directories - each user in our group gets there own work folder to store there own things without the file storage limit.


## Using Conda:
Conda Environments for the Lab


#### What is Conda (and why we use it)

Here is a video overview of what conda is... [https://youtu.be/sDCtY9Z1bqE?si=pgRFDddbxCM26KxW](url)

Conda is a package and environment manager. It lets you:

install software (R/Python + libraries, CLI tools) without admin rights,

keep multiple, isolated environments (different versions for different projects),

make work reproducible by saving and restoring environment definitions.

We strongly recommend using mamba (a drop-in faster Conda replacement) for speed. You can still activate environments with conda activate … even if you install them with mamba.

#### Lab Policy: Per-User vs Shared Environments
  Per-User (in Home)

  Each user can create their own environments in Home for personal work.

  Pros: freedom to experiment.

#### Shared (group-maintained)

The lab maintains read-only, group environments for critical pipelines under:

```{bash}
/stor/work/Sedio/conda_envs
```

Pros: identical, reproducible setups for everyone; large space; backed up.

Cons: only lab maintainers update these (by design).

Plan: You can have your personal envs in Home, but when running specific, standardized parts of the pipeline, activate the shared env.

One-Time Setup (so shared envs show up automatically)

Add the shared env directory to your Conda search path and put Conda’s package cache in Scratch (saves Home quota):

### One Time Installing Conda:

Installing Conda + Mamba (per user, in Home)

Download and install Miniforge (recommended community build of Conda):

```{bash}
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o ~/miniforge.sh
bash ~/miniforge.sh -b -p ~/miniforge3
```

Initialize Conda for your shell:
```{bash}
source ~/miniforge3/etc/profile.d/conda.sh
conda init bash   # or zsh
exec $SHELL       # reload your shell
```

Install Mamba into base:
```{bash}
conda install -n base -c conda-forge mamba
```

(Optional) Configure defaults for reproducibility:
```{bash}
conda config --add channels conda-forge
conda config --set channel_priority strict
```
#### One-Time Setup (to see shared envs automatically)

Make sure Conda is initialized for your shell (see above).

Add the shared env directory to your Conda search path:

```{bash}
conda config --add envs_dirs /stor/work/Sedio/conda_envs
```

After this, conda env list will include the shared envs, and you’ll be able to do conda activate <name> if names are unique.

#### Using the Shared and personal conda Environments

You can list all of the environments that you have access to in your path using:

#### List environments (includes shared if envs_dirs is set)
```bash
conda env list
```
#### Activate an enironment

In order to use a specific environment you have to activate it:

Full Path:
You can activate by path (always works):
```bash
conda activate /stor/work/Sedio/conda_envs/<ENV_NAME>
```

If you added /stor/work/Sedio/conda_envs to envs_dirs, you can also:

```{bash}
conda activate <ENV_NAME>
```

#### Activate an enironment (go back to base env)

```{bash}
conda deactivate
```

#### Creating Your Own Environment (in Home)
##### Faster installs with mamba
```{bash}
mamba create -p ~/conda-envs/myproj python=3.11
conda activate ~/conda-envs/myproj
```

##### Install packages
```{bash}
mamba install numpy pandas jupyterlab
```

You can also install using pip:

```{bash}
pip install numpy pandas jupyterlab
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


#### Clone a shared environment to you local storage so you can edit it...

Clone it to your Home and modify locally. Note you do not have to clone in order to run common tasks but if you'd like to make changes to the pipeline you can clone it to test out those changes.

```{bash}
conda create -p ~/conda-envs/myproj --clone /stor/work/Sedio/conda_envs/<ENV_NAME>
conda activate ~/conda-envs/myproj
mamba install <extra-packages>
```

### Common Commands Cheat-Sheet

##### Activate an env by path (always works)
```{bash}
conda activate /stor/work/Sedio/conda_envs/<ENV_NAME>
```

##### Create a personal env in Home
```{bash}
mamba create -p ~/conda-envs/analysis python=3.11 r-base=4.3
```
##### Install packages
```{bash}
mamba install -p ~/conda-envs/analysis numpy scipy scikit-learn
```
##### Export (portable)
```{bash}
conda env export --no-builds -p ~/conda-envs/analysis > ~/analysis_env.yml
```
##### Recreate from YAML
```{bash}
mamba env create -p ~/conda-envs/analysis2 -f ~/analysis_env.yml
```
 
## software

/stor/work/Sedio/software/ is where we will install key software packages like sirius, mzmine msconver etc. 

If you would like to add a piece of software let us know

## github repos

It is often useful to down specific github repos and use them like you would a package. We will store shared ones here! If it's not going to be maintained for the group please put it in your home directory or  /stor/work/Sedio/user_directories/



