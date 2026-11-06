# Legacy

[Back to the main README](../README.md)

The `legacy/` directory contains older Bash-based scripts that predate the current Python implementation. They are kept for historical reference but are **no longer maintained or recommended**.

### `execution-metrics-collector.sh`

The original Bash wrapper for launching a command and monitoring it. It runs the command in the background, captures the PID, and calls `process-metrics-collector` directly:

```bash
./legacy/execution-metrics-collector.sh {base_metrics_directory} {command} {args...}
```

This has been superseded by `execution-metrics-collector`, which provides the same functionality in a more portable and maintainable way. The sample series included in this repository was originally collected using this script:

```bash
~/projects/treecript/legacy/execution-metrics-collector.sh \
  ~/projects/treecript/Wetlab2Variations_metrics \
  python WfExS-backend.py -L workflow_examples/local_config.yaml \
  staged-workdir offline-exec 01a1db90-1508-4bad-beb7-7f7989838542
```

### `plotGraph.sh`

The original gnuplot-based visualization script. It reads the collected CSV files and generates `.pdf` charts using `gnuplot` (requires `apt install gnuplot`). It has been superseded by `plotGraph`, which generates richer charts without requiring gnuplot.

```bash
./legacy/plotGraph.sh {metrics_csv_files...}
```

### `plot-metrics.sh`

An earlier helper script for plotting individual metric files. Also superseded by `plotGraph`.

> These scripts are no longer actively maintained. For all new usage, prefer the Python equivalents.

---
