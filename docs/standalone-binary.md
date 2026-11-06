# Standalone collector binary (PyInstaller)

[Back to the main README](../README.md) | [Installation](installation.md) | [Usage](usage.md)

Use this to run `execution-metrics-collector` without installing Python, pip,
or a container runtime on the target machine. [PyInstaller](https://pypi.org/project/pyinstaller/)
bundles the Python interpreter and application dependencies into one executable.
It still needs a compatible Linux system, architecture and glibc; see
[compatibility](#checking-glibc-compatibility-before-deploying).

#### Alternative A: Use a pre-built binary

A Docker-built binary of `execution-metrics-collector` is published as the OCI
artifact `ghcr.io/inab/treecript:exec-binary-linux-x86_64` in the repository's
[Packages](https://github.com/inab/treecript/pkgs/container/treecript). It is
distinct from the [Singularity runtime image](installation.md#option-1-singularity).

**What it is:** a Linux x86-64 single-file executable, built with PyInstaller
inside a `manylinux_2_28` container. Glibc 2.28 is the intended baseline, not a
guarantee that every bundled library works on every system. Verify the actual
artifact and test on the target system.

Binaries are pushed and pulled as [OCI artifacts](https://oras.land/) using [`oras`](https://oras.land/docs/installation), the same underlying tool `singularity pull oras://...` uses for the container images above.

**Downloading it:**

```bash
# Install oras once, if you don't have it: https://oras.land/docs/installation
# Access may require oras login if the package is private.
oras pull ghcr.io/inab/treecript:exec-binary-linux-x86_64

chmod +x execution-metrics-collector
./execution-metrics-collector
```

**Using it on an HPC cluster:** it can be pulled and run on a compatible login
node, or inside an interactive Slurm allocation:

```bash
# Option A: pull and run directly on the login node
oras pull ghcr.io/inab/treecript:exec-binary-linux-x86_64
chmod +x execution-metrics-collector
./execution-metrics-collector ~/my_metrics my_command --arg1 --arg2

# Option B: interactive job via Slurm (salloc) — recommended for anything
# that needs dedicated compute resources rather than sharing the login node
salloc -n 1 -c 4 -t 00:30:00   # adjust cores/time/partition to your cluster
# once the allocation starts and you're placed on a compute node:
./execution-metrics-collector ~/my_metrics my_command --arg1 --arg2
exit   # ends the salloc session when done
```

Before relying on this binary on a new target machine, check architecture and
glibc on the actual compute node as described [below](#checking-glibc-compatibility-before-deploying):

```bash
uname -m
ldd --version | head -1
```

An older glibc or a different architecture needs another compatible build; the
recipes below target x86-64 and do not automatically support older systems.

**Publishing a new version (maintainers):**

```bash
# 1. Log in to GitHub Container Registry (needs a PAT with write:packages scope)
echo "$GITHUB_TOKEN" | oras login ghcr.io -u your-github-username --password-stdin

# 2. Build the binary (see "Building the binary" below), then push it as an
#    OCI artifact — no Dockerfile/container involved, just the raw file
oras push ghcr.io/inab/treecript:exec-binary-linux-x86_64 \
  dist/execution-metrics-collector:application/octet-stream

# 3. Confirm it shows up under the repository's Packages tab
```

Avoid overwriting an existing tag with an untested build. If publishing a second
binary, use a distinct tag identifying the treecript commit, architecture,
glibc baseline and builder, and provide checksums and test results. A separate
Apptainer-built artifact is not necessary when it offers no tested compatibility
or reproducibility advantage over the existing Docker-built binary.

#### Alternative B: Building it yourself

##### Why use a build container

The binary must be built on a machine whose **glibc version is equal to or older than** the target machine's glibc, because glibc is forward-compatible but not backward-compatible: a binary built against a newer glibc will refuse to run on a system with an older one, failing with an error such as:

```
/lib64/libc.so.6: version `GLIBC_2.35' not found (required by execution-metrics-collector)
```

Development laptops typically run a fairly recent Linux distribution (e.g. Ubuntu 22.04, glibc 2.35), while HPC login/compute nodes often run older, more conservative distributions (e.g. glibc 2.28–2.34). Building directly on the laptop would therefore very likely produce a binary that cannot run on the cluster.

One approach is to build inside a [`manylinux`](https://github.com/pypa/manylinux)
container, which provides a defined glibc baseline:

```bash
# Check your target machine's glibc version:
ssh your-user@your-hpc-login-node "ldd --version | head -1"

# Check your build machine's glibc version:
ldd --version | head -1
```

If the target's glibc is older than the build host's, choose a compatible build
environment. These recipes use `manylinux_2_28_x86_64`; supporting an older
glibc or another architecture requires adapting and testing the recipe and
its dependencies, not merely changing the image name.

> **Note:** the Python interpreters preinstalled inside `manylinux` images (under `/opt/python/cpXXX-cpXXX`) are built **without** a shared `libpython` — they are meant for compiling wheels, not for running applications. PyInstaller requires a shared `libpythonX.Y.so`, so the container build compiles its own Python from source with `--enable-shared`. It also needs `openssl-devel` (and other `-devel` headers) installed **before** compiling Python, otherwise Python's `ssl` module is silently skipped and `pip` cannot reach PyPI.

##### Build with Apptainer or Singularity

The [builder definition](../treecript-builder.def) builds a **builder image**;
it is not the [runtime image](../installation/Singularity.def). Its `Bootstrap:
docker` line fetches an OCI base image; a Docker daemon is not required.
Run the following from the repository root on Linux x86-64, with Apptainer
installed, network access, and sufficient disk space. Building from a definition
file requires root, a working fakeroot configuration, or another supported
build service; check the cluster's policy. Singularity can be used instead by
replacing `apptainer` with `singularity` if its version supports these options.

The definition expects `constraints-3.12.txt` in the build context, not in
`installation/`. Stage a copy without changing the source files:

```bash
mkdir -p build/pyinstaller-context build/pyinstaller-output
cp treecript-builder.def build/pyinstaller-context/
cp installation/constraints-3.12.txt build/pyinstaller-context/
(
  cd build/pyinstaller-context
  apptainer build --fakeroot --build-arg TREECRIPT_REF=exec \
    treecript-builder.sif treecript-builder.def
)

# The runscript writes build/, dist/ and a .spec file to /work.
apptainer run --bind "$PWD/build/pyinstaller-output:/work" --pwd /work \
  build/pyinstaller-context/treecript-builder.sif

build/pyinstaller-output/dist/execution-metrics-collector
```

The final command should print usage and exit with status 1 because no arguments
were provided; also test a real workload on the target.
The recipe installs the **remote** `TREECRIPT_REF` (default `exec`), not
uncommitted local changes. Override `TREECRIPT_GIT_URL` and `TREECRIPT_REF`
with `--build-arg` to select a repository and preferably an immutable commit.
Record that commit and the image/dependency versions with the artifact.

The recipe compiles Python 3.13.9 but uses the repository's 3.12 constraints
file. If changing `PYVER`, also update the hard-coded `python3.13` executable
and select appropriate constraints; do not assume arbitrary Python versions
will work. During `%post`, it explicitly exports `LD_LIBRARY_PATH` because
`%environment` applies at runtime, not while building the image.

##### Build with Docker

Save the following as `Dockerfile` in a build directory containing a copy of
`installation/constraints-3.12.txt` named `constraints-3.12.txt`. Like the
Apptainer definition, this example uses Python 3.13 with 3.12 constraints and
installs the selected remote ref, not local changes.

```dockerfile
FROM quay.io/pypa/manylinux_2_28_x86_64

ARG PYVER=3.13.9
ARG TREECRIPT_GIT_URL=https://github.com/inab/treecript.git
ARG TREECRIPT_REF=exec

ENV PYSHARED_PREFIX=/opt/python-shared
ENV LD_LIBRARY_PATH=${PYSHARED_PREFIX}/lib

# Build-time dependencies for compiling Python (openssl-devel is required,
# otherwise Python ends up without the ssl module and pip cannot reach PyPI)
RUN dnf install -y \
        openssl-devel bzip2-devel libffi-devel zlib-devel xz-devel \
        ncurses-devel readline-devel sqlite-devel tk-devel gdbm-devel \
    && dnf clean all

# Compile Python with --enable-shared, required by PyInstaller
RUN curl -O https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tgz \
    && tar xzf Python-${PYVER}.tgz \
    && cd Python-${PYVER} \
    && ./configure --enable-shared --prefix=${PYSHARED_PREFIX} --with-openssl=/usr \
    && make -j"$(nproc)" \
    && make altinstall \
    && cd .. && rm -rf Python-${PYVER} Python-${PYVER}.tgz

ENV PYBIN=${PYSHARED_PREFIX}/bin/python3.13
WORKDIR /src

RUN ${PYBIN} -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY constraints-3.12.txt /src/constraints-3.12.txt

RUN /opt/venv/bin/pip install --upgrade pip wheel \
    && /opt/venv/bin/pip install -c /src/constraints-3.12.txt \
       "treecript[analytics,docker] @ git+${TREECRIPT_GIT_URL}@${TREECRIPT_REF}" \
    && /opt/venv/bin/pip install pyinstaller

CMD ["/opt/venv/bin/pyinstaller", "-F", "-n", "execution-metrics-collector", \
     "/opt/venv/bin/execution-metrics-collector"]
```

Build the image once (this recompiles Python from source, so it takes several minutes the first time; subsequent builds reuse the cached layer as long as `PYVER` doesn't change):

```bash
docker build -t treecript-builder \
  --build-arg TREECRIPT_GIT_URL=https://github.com/inab/treecript.git \
  --build-arg TREECRIPT_REF=exec \
  -f Dockerfile .
```

Then generate the binary itself (fast — reuses the already-built image):

```bash
docker run --rm -v "$PWD/dist:/src/dist" treecript-builder
```

The resulting `dist/execution-metrics-collector` is a single, self-contained executable (`--onefile` / `-F` build).

> **Why only `execution-metrics-collector`?** The binary is for collection on
> a node without Python. Run the analysis tools afterwards in a separate
> [Python environment](installation.md), as in the
> [full workflow example](#full-workflow-example-hpc-metrics-collection--local-analysis).

##### Checking glibc compatibility before deploying

Check the executable's architecture and the glibc symbols required by its
outer PyInstaller bootloader (adjust the path for the Apptainer output):

```bash
file dist/execution-metrics-collector
objdump -T dist/execution-metrics-collector | grep GLIBC_ \
  | sed 's/.*GLIBC_\([0-9.]*\).*/\1/' | sort -V | tail -1
```

The reported version must not exceed the target's glibc, but this check alone
is **not sufficient**: one-file bundles also contain native libraries whose
requirements are not checked by `objdump` on the outer executable. Verify
those libraries separately and test a representative collection on the actual
compute nodes. Other system libraries, kernel features, permissions, and CPU
instruction sets can also affect compatibility. PyInstaller extracts a one-file
bundle at startup; its temporary directory must be writable and permit execution.

##### Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `version 'GLIBC_2.XX' not found` when running the binary | The bootloader or a bundled library requires newer glibc than the target | Adapt the build and dependencies for an older compatible environment, then test on the target |
| `Python was built without a shared library` during `pyinstaller` build | Using the manylinux-provided Python instead of a `--enable-shared` build | Compile Python from source with `--enable-shared`, as shown above |
| `SSL module is not available` / pip cannot reach PyPI while building the image | `openssl-devel` (and related `-devel` headers) missing before compiling Python | Install `openssl-devel` (and the other `-devel` packages listed above) before the `./configure && make` step |
| Files generated by `docker run` are root-owned | The container runs as `root` | Run with an appropriate user and writable working directory, or ask an administrator to correct ownership |
| Apptainer build fails with a fakeroot error | Fakeroot is unavailable or not configured | Ask the administrator about fakeroot or a supported build service |
| One-file binary fails while extracting or loading libraries | Temporary directory is not writable or is mounted `noexec` | Set `TMPDIR` to a writable executable filesystem allowed by cluster policy |

#### Full workflow example: HPC metrics collection + local analysis

Build with either method above or download the published artifact, then check
compatibility before copying it to the cluster. For example, from the repository
root after the Apptainer build:

```bash
scp build/pyinstaller-output/dist/execution-metrics-collector your-user@your-hpc-login-node:~/
ssh your-user@your-hpc-login-node
```

On the cluster, check the target compute node and follow its job policy:

```bash
chmod +x execution-metrics-collector
salloc -n 1 -c 4 -t 00:30:00  # adjust to your cluster
uname -m
ldd --version | head -1
./execution-metrics-collector ~/my_metrics my_command --arg1 --arg2
exit  # end the allocation; then exit the SSH session
```

Back on the laptop, replace the example run directory with the one created on
the cluster. Install a separate [Python environment](installation.md) for
analysis, and activate it before running these commands:

```bash
RUN=2025_01_01-00_00-12345
mkdir -p my_metrics
scp -r "your-user@your-hpc-login-node:my_metrics/$RUN" my_metrics/
git clone https://github.com/JosuaCarl/cpu-spec-dataset cpu-spec-dataset_Josua
plotGraph "my_metrics/$RUN" my_charts/
tdp-finder "my_metrics/$RUN" cpu-spec-dataset_Josua/dataset/*.csv
# Replace 350.0 with the TDP found for your compute node, in watts.
metrics-aggregator "my_metrics/$RUN" my_agg/ 350.0
```

> **Tip:** if `tdp-finder` prints `Unable to match a valid processor row` for some of the CSV sources you passed, that's normal — different sources use slightly different naming conventions for the same CPU. `tdp-finder` tries each file in order and stops at the first match; passing several sources increases the odds of a hit. The official vendor CSVs (e.g. `intel-cpus.csv`) tend to be the most reliable matches.

---
