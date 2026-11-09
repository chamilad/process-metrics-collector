# Usage and CPU datasets

[Back to the main README](../README.md) | [Metrics reference](metrics.md)

Run the examples from the repository root.

## Quick Start (Singularity/Apptainer)

This example uses the [collection runtime image](installation.md#option-1-singularity),
not the [PyInstaller builder image](standalone-binary.md#build-with-apptainer-or-singularity).
The runtime image is currently limited to metrics gathering.

```bash
# 1. Collect metrics for a command in background
my_command --arg1 --arg2 &

# bash puts the PID of the last background process in $!
singularity exec treecript-exec.sif process-metrics-collector $! ~/my_metrics
```

## Quick Start (other options)

```bash
# 1. Collect metrics for a command
execution-metrics-collector ~/my_metrics my_command --arg1 --arg2

# 2. Plot time series charts
plotGraph ~/my_metrics/2025_01_01-00_00-12345/ ~/my_charts/

# 3. Find your CPU's TDP
tdp-finder ~/my_metrics/2025_01_01-00_00-12345/ cpu-spec-dataset_Josua/dataset/*.csv

# 4. Aggregate and estimate energy consumption
metrics-aggregator ~/my_metrics/2025_01_01-00_00-12345/ ~/my_agg/ 28.0
```

---

## Programs Reference

### Collecting metrics

`execution-metrics-collector` runs a command and monitors it and all its child processes:

```bash
execution-metrics-collector {base_metrics_directory} {command} {args...}
```

Internally this launches the command, captures its PID, and calls `process-metrics-collector` with a sampling period of 1 second:

```bash
process-metrics-collector {pid} {base_metrics_directory} [sample_period]
```

Example:

```bash
execution-metrics-collector ~/metrics python myscript.py --input data.txt
```

---

### Plotting time series charts

`plotGraph` generates line charts for each monitored process, comparing time series of CPU, memory, I/O and other metrics:

```bash
plotGraph {metrics_directory} {output_directory}
```

Example:

```bash
plotGraph ~/metrics/2025_01_01-00_00-12345/ ~/charts/
```

---

### Finding CPU TDP

Three programs are available depending on what information you have:

#### `tdp-finder` — from a metrics directory

```bash
tdp-finder {metrics_directory} {csv_files...}
```

Example:

```bash
tdp-finder ~/metrics/2025_01_01-00_00-12345/ cpu-spec-dataset_Josua/dataset/*.csv cpumark_table.csv
```

Use `-q` for quiet mode (outputs only the TDP value, useful for scripting):

```bash
tdp-finder -q ~/metrics/2025_01_01-00_00-12345/ cpu-spec-dataset_Josua/dataset/*.csv
# Output: 28.0
```

#### `cpuinfo-tdp-finder` — from `/proc/cpuinfo`

Does not require a metrics directory:

```bash
cpuinfo-tdp-finder /proc/cpuinfo cpu-spec-dataset_Josua/dataset/*.csv cpumark_table.csv
```

Or from a saved copy of `/proc/cpuinfo` — the `sample_cpuinfo/` directory contains example files for Intel and AMD processors you can use for testing:

```bash
cpuinfo-tdp-finder sample_cpuinfo/cpuinfo-amd.txt cpu-spec-dataset_Josua/dataset/*.csv
```

#### `modelname-tdp-finder` — from a processor model string

```bash
modelname-tdp-finder "11th Gen Intel(R) Core(TM) i7-1185G7 @ 3.00GHz" cpu-spec-dataset_Josua/dataset/*.csv
modelname-tdp-finder "AMD EPYC 7742 64-Core Processor" cpu-spec-dataset_Josua/dataset/*.csv cpumark_table.csv
```

---

### Digesting metrics

`metrics-aggregator` digests the collected time series and estimates energy consumption per process subtree. It requires the CPU TDP value in Watts.

```bash
metrics-aggregator {metrics_directory} {output_directory} {TDP_watts} [command_filter]
```

The optional `command_filter` argument filters results to show only processes whose command matches the string (e.g. `"docker run"` to focus on Docker steps).

Example using the included sample series:

```bash
metrics-aggregator sample-series/Wetlab2Variations_metrics/2025_05_20-02_19-14001/ dest_directory 28.0 "docker run"
```

The output directory will contain:

- A table of energy consumption per task (stdout)
- `graph.pdf` / `graph.svg` — process call graph as a tree
- `spiral-graph.pdf` / `spiral-graph.svg` — process call graph as a spiral
- `consumptions.pdf` / `consumptions.svg` — barplot of task energy and duration
- `timeline.pdf` / `timeline.svg` — lollipop chart of task start, duration, and end

![Sample process call graph (tree)](../sample-charts/graph.svg)
![Sample process call graph (spiral)](../sample-charts/spiral-graph.svg)
![Sample task consumptions and duration barplots](../sample-charts/consumptions.svg)
![Sample task executions lollipop](../sample-charts/timeline.svg)

---

## CPU Dataset Setup

The TDP programs require one or more CPU specification datasets to look up processor TDP values. Three sources are supported:

**Recommended — JosuaCarl fork** (better column names):

```bash
git clone https://github.com/JosuaCarl/cpu-spec-dataset cpu-spec-dataset_Josua
```

**Alternative — original felixsteinke repo:**

```bash
git clone https://github.com/felixsteinke/cpu-spec-dataset
```

**CPUBenchmark scrape** (good coverage for AMD server CPUs):

```bash
python -m treecript.tdp_sources cpumark_table.csv
```

You can pass multiple sources to the TDP programs and they will be tried in order:

```bash
tdp-finder ~/metrics/dir/ cpu-spec-dataset_Josua/dataset/*.csv cpumark_table.csv
```

> **Tip:** if `tdp-finder` logs `Unable to match a valid processor row` for one of your CSV sources, that's usually just that particular source's naming convention not matching your `/proc/cpuinfo` model string exactly (e.g. extra vendor symbols, or `[Dual CPU]` prefixes for multi-socket listings). This is expected when passing several sources — `tdp-finder` simply moves on to the next file until it finds a match. The `intel-cpus.csv` / `ampere-cpus.csv` sources (official vendor data) tend to match most reliably for their respective vendors.

---
