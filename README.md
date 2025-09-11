# <div align="center"> Sedio Lab Group Metabolomics Pipeline </div>
## <div align="center"> Using the UT Austin Biomedical Research Computing Facility (BRCF) - aka Pods </div>


## Table of Contents
- [ Sedio Lab Group Metabolomics Pipeline ](#-sedio-lab-group-metabolomics-pipeline-)
  - [ Using the UT Austin Biomedical Research Computing Facility (BRCF) - aka Pods ](#-using-the-ut-austin-biomedical-research-computing-facility-brcf---aka-pods-)
  - [Table of Contents](#table-of-contents)
    - [Create Your POD Account](#create-your-pod-account)
    - [Connecting to CPU Rental Pods:](#connecting-to-cpu-rental-pods)
  - [1. Connecting to a Remote Server through the browser using ondemand](#1-connecting-to-a-remote-server-through-the-browser-using-ondemand)
      - [2. Connecting to a Remote Server with VS Code](#2-connecting-to-a-remote-server-with-vs-code)
      - [Prerequisites](#prerequisites)
      - [Step 1: Install the "Remote - SSH" Extension](#step-1-install-the-remote---ssh-extension)
      - [Step 2: Connect to the Remote Server](#step-2-connect-to-the-remote-server)
      - [Step 3: Authenticate and Connect](#step-3-authenticate-and-connect)
      - [Step 4: Open a Folder on the Remote Server](#step-4-open-a-folder-on-the-remote-server)
### Create Your POD Account

1.  Request a POD account [here](https://rctf-account-request.icmb.utexas.edu/). You can also learn more about POD resources [here](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers/pages/31976153/POD+Accounts).

2.  In the "Affiliation" field, select "Sedio_Brian". Please note that it may take 1-2 days for your account to be activated for SSH access to the computing clusters.

This will get you access to the rental pods which have large CPU's, storage and memory. It is also where we have preinstall key softwore for the metabolomics pipeline.

    1.  `rentcomp01.ccbb.utexas.edu` (CPU: 72 threads, Memory: 754G)
    2.  `rentcomp02.ccbb.utexas.edu` (CPU: 72 threads, Memory: 251G)
    3.  `rentcomp03.ccbb.utexas.edu` (CPU: 112 threads, Memory: 754G)

If you need access to GPUs for machine learning pipelines please reach out to Dale Forrister, we have limited access to this but only for tasks that actually benefit from GPUs.

### Connecting to CPU Rental Pods:

## 1. Connecting to a Remote Server through the browser using ondemand

This is by far the easiest way to connect. It is also the best way to run R on the server. I generally prefer vscode for python rather than Jupyterhub but you can explore both options.

Follow this link depending on which compute node you are are targeting.

 [https://rentcomp1.ccbb.utexas.edu/](https://rentcomp01.ccbb.utexas.edu/)
 
 [https://rentcomp2.ccbb.utexas.edu/](https://rentcomp02.ccbb.utexas.edu/)

 [https://rentcomp3.ccbb.utexas.edu/](https://rentcomp03.ccbb.utexas.edu/)

  You can choose between:
  RStudio
  Jupyterhub

  When you are coding here you will be running on the cluster through web browser


#### 2. Connecting to a Remote Server with VS Code

Visual Studio Code, a powerful and versatile code editor, can be transformed into a robust remote development environment. By connecting to a remote server, you can edit files and run commands as if you were working directly on that machine. This tutorial will guide you through connecting to a server using the popular "Remote - SSH" extension.

#### Prerequisites

Before you begin, make sure you have installed Visual Studio Code (VS Code). You can find installation tutorials here:

  * **Windows**: [How to install Visual Studio Code on Windows 10/11](https://www.youtube.com/watch?v=2Gz-uuQWxu4)
  * **macOS**: [How to Install Visual Studio Code on Mac](https://www.youtube.com/watch?v=w0xBQHKjoGo)

It is also recommended that you read the first two parts of ["Practical Computing for Biologists" by Haddock and Dunn](<docs/Practical Computing for Biologists.pdf>) to learn the basics of Linux and the Shell.


3.  We currently have three nodes available on POD (server addresses listed below):

4.  These nodes are shared with other labs, so please be mindful of your resource usage to avoid overloading the system. The POD manager will restrict processes that use excessive resources. You may receive an email notification like this:

    ```
    The process: [PID: 2136120] /stor/home/bf22265/micromamba/envs/dreams/bin/python
    owned by bf22265 (UID: 601015) has been modified:

    This process was reniced for excess CPU time usage
    The current nice value of this process is 19
    This process has consumed 204 minutes of CPU time.
    ```

#### Step 1: Install the "Remote - SSH" Extension

1.  Open **VS Code**.
2.  Navigate to the **Extensions** view by clicking the square icon in the sidebar on the left, or by pressing `Ctrl+Shift+X` (Windows) or `Cmd+Shift+X` (macOS).
3.  In the search bar, type `Remote - SSH`.
4.  Locate the extension provided by **Microsoft** and click the **Install** button.

#### Step 2: Connect to the Remote Server

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

#### Step 3: Authenticate and Connect

1.  After adding the host, it will appear in your list of SSH Targets in the Remote Explorer.

2.  Hover over the host you just added and click the **Connect to Host in New Window** icon (it looks like a folder with a plus sign).

3.  A new VS Code window will open. If this is your first time connecting, you may be prompted to confirm the server's fingerprint. Type `yes` and press **Enter**.

4.  Next, you will be prompted for your password. Enter your POD account password and press **Enter**.

      * **Note on SSH Keys:** If you have configured an SSH key for your server, you may not be prompted for a password. You can learn more about passwordless access [here](https://cloud.wikis.utexas.edu/wiki/spaces/RCTFusers/pages/31976509/POD+Resources+and+Access).

5.  Once the connection is successful, you will see your server's address in the green status bar at the bottom-left corner of the VS Code window. This indicates that you are now working on the remote server.

#### Step 4: Open a Folder on the Remote Server

Now that you are connected, you can open a project folder from the remote server.

1.  Click **Open Folder** in the Explorer sidebar.
2.  A dialog will appear showing the file system of your remote server.
3.  Navigate to the directory you want to work in, select it, and click **OK**.

The folder's contents will appear in the VS Code Explorer. You can now create, edit, and delete files on your remote server directly from VS Code. The integrated terminal (`Ctrl+Shift+~`) will also now open a terminal session on your remote server.

Congratulations! You have successfully connected to a remote server with VS Code. You can now enjoy a seamless remote development experience with the full power of your favorite editor.




