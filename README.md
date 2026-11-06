# `treecript`: Process Tree Metrics Transcriptor

Originally named *Execution Process Metrics Collector*, treecript monitors Linux
processes and their descendants, collects their metrics, and helps analyze and
visualize the results. It was initially developed for
[ELIXIR STEERS](https://elixir-europe.org/about-us/how-funded/eu-projects/steers).

## Documentation

- [Installation](docs/installation.md): Singularity/Apptainer, pip, and Conda.
- [Standalone collector binary](docs/standalone-binary.md): download the existing
  Docker-built binary, build with Docker or Apptainer/Singularity, and check
  compatibility with HPC systems.
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

## Repository

The Python package is in `treecript/`, installation recipes and constraints are
in `installation/`, and examples are in `sample-series/`, `sample-charts/`,
`sample-work-to-measure/`, and `onboarding/`. Tests are in `tests/`.

## License

Licensed under GNU GPL v3. This repository is a fork and evolution of
[chamilad/process-metrics-collector](https://github.com/chamilad/process-metrics-collector).
