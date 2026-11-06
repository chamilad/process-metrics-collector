# Output files and metrics

[Back to the main README](../README.md) | [Usage](usage.md)

Each `execution-metrics-collector` run creates a subdirectory named after the start timestamp and PID. It contains:

| File                               | Description                                                    |
| ----------------------------------- | -------------------------------------------------------------- |
| `reference_pid.txt`                | PID of the root process being monitored                        |
| `sampling-rate-seconds.txt`        | Sampling rate in seconds (usually 1)                           |
| `pids.txt`                         | Table of all spawned processes with timestamps and parent PIDs |
| `agg_metrics.tsv`                  | Time series of aggregated metrics across all processes         |
| `metrics-{pid}_{create_time}.csv`  | Per-process time series metrics                                |
| `command-{pid}_{create_time}.txt`  | Linearized command line for each process                       |
| `command-{pid}_{create_time}.json` | JSON representation of the command line                        |
| `cpu_details.json`                 | Physical CPU information from `/proc/cpuinfo`                  |
| `core_affinity.json`               | Processor-to-core-to-CPU mapping derived from `/proc/cpuinfo`  |

### Per-process metrics (`metrics-{pid}_{create_time}.csv`)

| Column            | Description                                                                   |
| ----------------- | ------------------------------------------------------------------------------ |
| `Time`            | Sample timestamp                                                              |
| `PID`             | Process ID                                                                    |
| `Virt`            | Virtual memory size (matches `top` VIRT)                                      |
| `Res`             | Resident set size — non-swapped physical memory (matches `top` RES)           |
| `CPU`             | CPU utilization as a percentage (can exceed 100% for multithreaded processes) |
| `Memory`          | RSS memory as a percentage of total physical system memory                    |
| `TCP connections` | Number of open TCP connections                                                |
| `Thread Count`    | Number of threads (non-cumulative)                                            |
| `User`            | Time spent in user mode (seconds)                                             |
| `System`          | Time spent in kernel mode (seconds)                                           |
| `Children_User`   | User time of child processes (always 0 on Windows/macOS)                      |
| `Children_System` | System time of child processes (always 0 on Windows/macOS)                    |
| `IO`              | Time waiting for blocking I/O (Linux only)                                    |
| `uss`             | Unique Set Size — memory freed if this process terminated now                 |
| `swap`            | Memory swapped out to disk                                                    |
| `processor_num`   | Number of unique CPU processors used                                          |
| `core_num`        | Number of unique CPU cores used                                               |
| `cpu_num`         | Number of unique physical CPUs used                                           |
| `processor_ids`   | IDs of CPU processors used (space-separated)                                  |
| `core_ids`        | IDs of CPU cores used (space-separated)                                       |
| `cpu_ids`         | IDs of physical CPUs used (space-separated)                                   |
| `process_status`  | Process status string (e.g. `sleeping`, `running`)                            |
| `read_count`      | Cumulative number of read syscalls                                            |
| `write_count`     | Cumulative number of write syscalls                                           |
| `read_bytes`      | Bytes physically read from disk (cumulative)                                  |
| `write_bytes`     | Bytes physically written to disk (cumulative)                                 |
| `read_chars`      | Bytes passed to read syscalls (cumulative, Linux only)                        |
| `write_chars`     | Bytes passed to write syscalls (cumulative, Linux only)                       |

### Aggregated metrics (`agg_metrics.tsv`)

Each row is a 1-second sample across all monitored processes combined:

| Column         | Description                              |
| -------------- | ----------------------------------------- |
| Timestamp      | Sample time                              |
| Number of PIDs | Processes monitored at that moment       |
| Threads        | Total thread count                       |
| Processors     | Number of distinct CPU processors in use |
| Cores          | Number of distinct CPU cores in use      |
| Physical CPUs  | Number of distinct physical CPUs in use  |
| CPU IDs        | IDs of physical CPUs (space-separated)   |
| User memory    | Total user memory across all processes   |
| Swap memory    | Total swap memory across all processes   |
| Read ops       | Total read operations                    |
| Write ops      | Total write operations                   |
| Read bytes     | Bytes physically read                    |
| Write bytes    | Bytes physically written                 |
| Read chars     | Bytes passed to read syscalls            |
| Write chars    | Bytes passed to write syscalls           |

---
