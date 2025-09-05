#### Sedio Lab Group Metabolomics Pipeline Using the UT Austin Biomedical Research Computing Facility (BRCF) - aka Pods

# Sedio Lab has access to CPU Rental Pods. To get get access 
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

#### Shared Work and Scratch areas
Shared Work and Scratch areas are available for each POD group under /stor/work/<GroupName> and /stor/scratch/<GroupName> (for example, /stor/work/Hofmann, /stor/scratch/Hofmann). These areas are accessible only by members of the named group. Users can find out which group or groups they belong to by typing the groups command on the command line.

These Work and Scratch areas are designed for storage of shared project artifacts, so they have no predefined structure (i.e. user directories are not automatically created). Group members may create any directory structure that is meaningful to the group's work.

Shared Work areas are backed up weekly. Scratch areas are not backed up. Both Work and Scratch areas may have quotas, depending on the POD (e.g. on the Rental or GSAF pod); such quotas are generally in the multi-terabyte range.

Because it has a large quota and is regularly backed up and archived, your group's Work area is where large research artifacts that need to be preserved should be located.

Scratch, on the other hand, can be used for artifacts that are transient or can easily be re-created (such as downloads from public databases).

See Manage storage areas by project activity for important guidelines for Work and Scratch area contents.

Weekly backups
All Home and Work directories are backed up weekly to a separate backup storage server (spinning disk). Backups take place sometime between Friday and Monday mornings and are currently not incremental backups.

Note that any directory in any file system tree named tmp, temp, or backups is not backed up. Directories with these names are intended for temporary files, especially large numbers of small temporary files. See "Cannot create tempfile" error and Avoid having too many small files.

Periodic and long-term archiving
Data on the backup server are periodically archived to TACC's Ranch tape archive roughly once a year. Current archives are as of:

2025-01 (in progress)
2024-01 (many but not all PODs)
2022-01
2020-07
In addition, to avoid re-archiving the same directories multiple times, we maintain a "long term archives (LTA)" directory that contains data from projects that are no longer active. Such project data may have been transferred to a group's Scratch area to avoid consuming backup space, or may have been removed from POD storage entirely after archiving to avoid consuming storage server space.

Please Contact Us if you need something retrieved from tape archives.




#Work Folder Structure:
conda_envs -
software - 


#Using Conda -
  #how to install to home directory

#Setting up Alius to Shared Conda Environments

  

#Converting raw files
#processing with Mzmine
#Sirius
#dreams

etc etc

