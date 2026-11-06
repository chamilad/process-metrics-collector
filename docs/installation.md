# Installation

[Back to the main README](../README.md)

### Prerequisites (singularity)

- Linux OS
- [Singularity](https://sylabs.io/docs/) or [Apptainer](https://apptainer.org/).

### Prerequisites (native)

- Linux OS (Ubuntu recommended)
- Python 3.9 or newer
- Git

### Not sure which installation method to use?

| I want to...                                                                   | Use                                                            |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| Keep things simple, already have either Apptainer or Singularity installed and you only want to gather metrics  | **Option 1 — Singularity**                                     |
| Keep things simple and already have Python installed                           | **Option 2 — pip + venv**                                      |
| Already use conda or manage multiple projects/environments                     | **Option 3 — Conda**                                           |
| Work on an HPC or shared cluster environment (e.g. BSC)                        | **Option 1 — Singularity** or **Option 3 — Conda**             |
| Deploy a standalone executable to a machine without Python or a container runtime | [Option 4 — Standalone binary (PyInstaller)](standalone-binary.md) |
| Work on a machine with a corporate or university firewall                      | Either — both have firewall notes in their respective sections |

---

### Choosing a constraints file (only needed for option 2, option 3 or option 4)

The repository ships per-version constraints files under the `installation/` directory to ensure a working set of dependencies. Pick the one that matches your setup (including the Python version):

| Situation                     | Constraints file to use                              |
| ----------------------------- | ---------------------------------------------------- |
| Native Linux, Python 3.x      | `installation/constraints-3.x.txt`                   |
| Ubuntu 22.04 on WSL (Windows) | `installation/constraints-3.x_Ubuntu-22.04-wsl.txt` |
| Ubuntu 24.04 on WSL (Windows) | `installation/constraints-3.x_Ubuntu-24.04-wsl.txt` |

> **WSL** = Windows Subsystem for Linux — Ubuntu running inside Windows rather than directly on hardware. If you are running Ubuntu natively on your machine, use the plain constraints file. To check:
>
> ```bash
> uname -r  # if the output contains "microsoft" or "WSL", you are on WSL
> ```

To check your Python version:

```bash
python3 --version
```

---

### Option 1: Singularity

#### Alternative A: Fetch a pre-built image (only for metrics gathering)

Pre-build singularity images are listed at https://github.com/inab/treecript/pkgs/container/treecript .

They can be fetched using Apptainer/Singularity just using `singularity pull` subcommand:

```bash
# Replace exec by the tag of the version you want to use 
singularity pull oras://ghcr.io/inab/treecript:exec

# The name of the created file depends on the tag
ls -l treecript-exec.sif
```

#### Alternative B: Building from source

When no file is locally, but you already have either Apptainer or Singularity installed:

```bash
# TREECRIPT_VER can be either a branch, a tag or a commit hash
TREECRIPT_VER=7c0a20a688518e43952d7bd7080bc34b863e32da

# If you don't have the recipe, you can fetch it using either curl or wget
mkdir -p treecript_SIF_build/installation
cd treecript_SIF_build/installation
curl -O https://raw.githubusercontent.com/inab/treecript/${TREECRIPT_VER}/installation/Singularity.def
cd ..
```

If you have already checked out the code

```bash
# Alternatively, you can use a checked out copy
cd treecript
TREECRIPT_VER=$(git rev-parse HEAD)
```

At last, you can build the SIF image with next command:

```
singularity build --build-arg treecript_checkout="${TREECRIPT_VER}" \
  treecript-${TREECRIPT_VER}.sif installation/Singularity.def 
```

---

### Option 2: pip + virtual environment (venv)

Use this if you already have Python installed on your system and don't use conda. This is the lightest option — it creates an isolated Python environment using only tools that come built into Python, with no additional software required.

```bash
# 1. Create a virtual environment
python3 -m venv TREECRIPT

# 2. Activate it
source TREECRIPT/bin/activate

# 3. Upgrade pip and wheel
pip install --upgrade pip wheel

# 4. Download the constraints file for your Python version (adjust filename as needed)
wget https://raw.githubusercontent.com/inab/treecript/exec/installation/constraints-3.10.txt

# 5. Install treecript with constraints
pip install -c constraints-3.10.txt 'treecript [analytics,docker] @ git+https://github.com/inab/treecript.git@exec'
```

> **Network issues?** Consult your network administrator about proxy and
> trusted certificate configuration.

To deactivate the environment:

```bash
deactivate
```

To reactivate later:

```bash
source TREECRIPT/bin/activate
```

---

### Option 3: Conda environment

Use this if you already work with Anaconda or Miniconda, or if you prefer conda for managing environments across multiple projects. Conda handles both Python and system-level dependencies, which makes it particularly well suited for HPC or shared computing environments.

#### Installing Miniconda (if not already installed)

Miniconda is a minimal conda installer — it gives you the `conda` command and Python without bundling hundreds of extra packages like the full Anaconda distribution does.

```bash
# Download installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh

# Run the installer
bash miniconda.sh
# - Accept the license
# - Accept the default install location
# - Answer "yes" when asked to update your shell profile

# Apply changes to current session
source ~/.bashrc

# Verify
conda --version
```

> **Network issues?** If `repo.anaconda.com` is blocked by your network, use **Miniforge** instead — it is functionally identical to Miniconda but downloads from GitHub and defaults to the `conda-forge` channel, which is actually a better fit for the scientific packages treecript needs:
>
> ```bash
> wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O miniconda.sh
> bash miniconda.sh
> ```

#### Creating the treecript conda environment

```bash
# 1. Create a clean environment with Python 3.10
conda create -n treecript python=3.10 -y

# 2. Activate it
conda activate treecript

# 3. Download the constraints file (adjust filename for your Python version / OS)
wget https://raw.githubusercontent.com/inab/treecript/exec/installation/constraints-3.10.txt
# or for WSL Ubuntu 22.04:
# wget https://raw.githubusercontent.com/inab/treecript/exec/installation/constraints-3.10_Ubuntu-22.04-wsl.txt

# 4. Install treecript and all dependencies in one shot
pip install -c constraints-3.10.txt 'treecript [analytics,docker] @ git+https://github.com/inab/treecript.git@exec'
```

To deactivate:

```bash
conda deactivate
```

To remove the environment entirely:

```bash
conda deactivate
conda remove -n treecript --all -y
```

---

### Option 4: Standalone binary

See the [standalone binary guide](standalone-binary.md) for the existing
Docker-built artifact, Apptainer/Singularity and Docker build instructions,
and system compatibility requirements.

### Verifying the installation

This check applies to a Python installation, including a separate environment
used to analyze metrics collected with the [standalone binary](standalone-binary.md).
It does not apply to the binary itself.

Run this after Option 2 (pip + venv) or Option 3 (Conda) — or after setting up the local analysis environment from Option 4's workflow example — to confirm all dependencies are working correctly:

```bash
python -c "
import psutil; print('psutil OK:', psutil.__version__)
import docker; print('docker OK:', docker.__version__)
import pandas; print('pandas OK:', pandas.__version__)
import networkx; print('networkx OK:', networkx.__version__)
import matplotlib; print('matplotlib OK:', matplotlib.__version__)
import adjustText; print('adjustText OK:', adjustText.__version__)
import treecript; print('treecript OK')
"
```

> To check the binary itself, run it with no arguments and confirm it prints
> its usage message; also test a representative collection on the target node.

---
