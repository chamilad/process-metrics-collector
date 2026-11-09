# `treecript`: Process Tree Metrics Transcriptor

Originally named *Execution Process Metrics Collector*, treecript monitors Linux
processes and their descendants, collects their metrics, and helps analyze and
visualize the results. It was initially developed for
[ELIXIR STEERS](https://elixir-europe.org/about-us/how-funded/eu-projects/steers).

## Documentation

The full list is in the [documentation index](docs/README.md).

- [Installation](docs/installation.md): Singularity/Apptainer, pip, and Conda.
- [Standalone collector binary](docs/standalone-binary.md): download the existing
  Docker-built binary, or use a builder image to create one with PyInstaller
  and check compatibility with HPC systems.
- [Usage and CPU datasets](docs/usage.md): collect, plot, find CPU TDP, and
  estimate energy consumption.
- [Metrics and output files](docs/metrics.md): output files and column reference.
- [RO-Crate representation](RO-Crate-REPRESENTATION.md): structure of generated
  RO-Crates.
- [Onboarding example](onboarding/README.md) and
  [sample workloads](sample-work-to-measure/README.md).
- [Legacy scripts](docs/legacy.md).

## Quick start

After a [Python installation](docs/installation.md#option-2-pip--virtual-environment-venv):

```bash
execution-metrics-collector ~/my_metrics my_command --arg1 --arg2
```

For container-based collection and subsequent analysis, see the
[usage guide](docs/usage.md). The standalone binary only provides the collector;
analysis requires a separate Python installation.

The Apptainer/Singularity [builder SIF](docs/standalone-binary.md#build-with-apptainer-or-singularity)
is an intermediate tool for producing that binary. It is not the separate
[collection runtime image](docs/installation.md#option-1-singularity).

## Repository

```text
treecript/
├── treecript/                  Python package (the actual implementation)
│   ├── collector.py            Process-tree metrics collection
│   ├── parser.py               Reads collected metrics
│   ├── aggregator.py           Digests metrics and estimates energy consumption
│   ├── plot_graph.py           Time series charts
│   ├── tdp_finder.py           CPU TDP lookup (uses tdp_sources.py)
│   ├── rocrate.py              RO-Crate generation
│   └── common.py               Shared helpers
├── *.py (top level)            Thin wrappers of the commands (see table below)
├── tests/                      Unit tests
├── docs/                       Documentation (start at docs/README.md)
├── installation/               Requirements, constraints and container recipes
├── treecript-builder.def       Apptainer/Singularity recipe for the standalone binary
├── setup.py, pyproject.toml    Packaging
├── data/                       Local CPU datasets (populated as in docs/usage.md)
├── legacy/                     Old Bash scripts (unmaintained)
├── onboarding/                 First installation and measurement walk-through
├── sample-work-to-measure/     Scripts that run sample workloads
├── sample/, sample-series/,    Example metrics, charts and CPU info files
│   sample-charts/, sample_cpuinfo/
└── .github/workflows/          CI: pre-commit, pip-audit, container builds
```

| Command | Module | Purpose |
|---------|--------|---------|
| `execution-metrics-collector` | `treecript.collector` | Run a command and collect its process tree metrics. |
| `process-metrics-collector` | `treecript.collector` | Collect metrics of an already running PID. |
| `plotGraph` | `treecript.plot_graph` | Plot time series charts.* |
| `metrics-aggregator` | `treecript.aggregator` | Aggregate metrics and estimate energy.* |
| `tdp-finder`, `cpuinfo-tdp-finder`, `modelname-tdp-finder` | `treecript.tdp_finder` | Find a CPU TDP from metrics, `/proc/cpuinfo` or a model name.* |

\* Needs the `analytics` extra (not included in the standalone binary).

The workflows in `.github/workflows/` are:

- `pre-commit.yml`, `pre-commit_wsl.yml`: linting, type checks, tests and licence checks.
- `pip-audit.yml`: scheduled security audit that regenerates the constraints files.
- `container.yml`, `container_self.yml`: Singularity/Apptainer image builds
  (on `v*` tags or manual dispatch).

## License

Licensed under GNU GPL v3. This repository is a fork and evolution of
[chamilad/process-metrics-collector](https://github.com/chamilad/process-metrics-collector).
