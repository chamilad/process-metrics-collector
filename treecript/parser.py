#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0-or-later
# treecript, a process tree metrics gatherer.
# Copyright (C) 2025 Barcelona Supercomputing Center, José M. Fernández
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import json
import logging
import os.path

from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        Optional,
        Sequence,
        Tuple,
    )

    import pathlib

import pandas as pd

from .common import (
    REFERENCE_PID_FILENAME,
    SAMPLING_PERIOD_FILENAME,
    PIDS_FILENAME,
    CPU_DETAILS_FILENAME,
    COMMAND_JSON_FILENAME_TEMPLATE,
    METRICS_CSV_FILENAME_TEMPLATE,
)

logger = logging.getLogger(__name__)

SINGLE_DOCKER_FLAGS = {
    "-d",
    "--detach",
    "--init",
    "-i",
    "--interactive",
    "--no-healthcheck",
    "--oom-kill-disable",
    "--privileged",
    "-P",
    "--publish-all",
    "-q",
    "--quiet",
    "--read-only",
    "--rm",
    "--sig-proxy",
    "-t",
    "--tty",
    "--use-api-socket",
    # A couple of common combinations
    "-ti",
    "-it",
}


def process_command(command: "Sequence[str]") -> "str":
    basename_command = os.path.basename(command[0])
    retlabel = basename_command
    if basename_command == "python":
        for i_token, token in enumerate(command[1:], 1):
            if not token.startswith("-"):
                retlabel += "\n" + os.path.basename(token)
                if retlabel == "cwltool":
                    retlabel += " " + command[i_token + 1]
                break
    elif basename_command == "java":
        for token in command[1:]:
            if not token.startswith("-"):
                retlabel += "\n" + os.path.basename(token)
                break
    elif basename_command == "docker":
        is_docker_run = False
        prev_flag = False
        for token in command[1:]:
            if is_docker_run:
                if token.startswith("-"):
                    prev_flag = token not in SINGLE_DOCKER_FLAGS
                elif prev_flag:
                    prev_flag = False
                else:
                    retlabel += "\n" + token
                    break
            elif token == "stats":
                retlabel = "docker stats"
                break
            elif token == "run":
                retlabel = "docker run"
                is_docker_run = True

    return retlabel


class MetricsParserException(Exception):
    pass


def metrics_parser(
    series_dir: "pathlib.Path",
    group_by_process_name: "Optional[str]" = None,
) -> "Tuple[float, pd.DataFrame, int, float]":
    if not series_dir.is_dir():
        errmsg = f"Path {series_dir.as_posix()} is not a directory"
        logger.error(errmsg)
        raise MetricsParserException(errmsg)

    reference_pid_filename = series_dir / REFERENCE_PID_FILENAME
    if not reference_pid_filename.is_file():
        errmsg = f"Path {reference_pid_filename.as_posix()} is not a filename"
        logger.error(errmsg)
        raise MetricsParserException(errmsg)

    with reference_pid_filename.open(mode="r", encoding="utf-8") as rF:
        reference_pid = float(rF.readline())

    sampling_period_filename = series_dir / SAMPLING_PERIOD_FILENAME
    if not sampling_period_filename.is_file():
        errmsg = f"Path {sampling_period_filename.as_posix()} is not a filename"
        logger.error(errmsg)
        raise MetricsParserException(errmsg)

    with sampling_period_filename.open(mode="r", encoding="utf-8") as sF:
        sampling_period_seconds = float(sF.readline())

    cpu_details_filename = series_dir / CPU_DETAILS_FILENAME
    if not cpu_details_filename.is_file():
        errmsg = f"Path {cpu_details_filename.as_posix()} is not a filename"
        logger.error(errmsg)
        raise MetricsParserException(errmsg)

    with cpu_details_filename.open(mode="r", encoding="utf-8") as cF:
        cpu_details = json.load(cF)

    # TODO, compute this per CPU
    num_cpu_cores = int(cpu_details[0]["cpu cores"])
    num_cpu_processors = len(cpu_details[0]["processors"])
    factor_cores_processors = float(num_cpu_cores) / float(num_cpu_processors)  # noqa: F841

    logger.info(
        f"Processing directory {series_dir.as_posix()} about pid {reference_pid}"
    )

    pids_filename = series_dir / PIDS_FILENAME
    if not pids_filename.is_file():
        errmsg = f"Path {pids_filename.as_posix()} is not a filename"
        logger.error(errmsg)
        raise MetricsParserException(errmsg)

    # Reading all the pids
    pids = pd.read_table(
        pids_filename,
        na_values=["-"],
        dtype={"PID": "Int32", "PPID": "Int32"},
        parse_dates=["Time"],
    )
    # Generating the needed columns to generate a tree structure
    pids["node"] = pids.apply(
        lambda row: str(row.create_time) + "_" + str(row.PID), axis=1
    )
    pids["parent"] = pids.apply(
        lambda row: (
            str(row.ppid_create_time) + "_" + str(row.PPID)
            if not pd.isna(row.PPID)
            else pd.NA
        ),
        axis=1,
    )

    # Now, let's read the command lines
    main_commands = []
    command_labels = []
    full_command = []
    full_stats = []
    subtree_root = []
    for index, row in pids.iterrows():
        command_json_filename = series_dir / COMMAND_JSON_FILENAME_TEMPLATE.format(
            row.PID, row.create_time
        )
        with command_json_filename.open(mode="r", encoding="utf-8") as cH:
            command_json = json.load(cH)
            assert isinstance(command_json, list)
            full_command.append(command_json)
            command = process_command(command_json)
            main_commands.append(command)
            command_labels.append(command + "\n" + str(index))
            subtree_root.append(
                command.startswith(group_by_process_name)
                if group_by_process_name is not None
                else row.PID == reference_pid
            )

        metrics_csv_filename = series_dir / METRICS_CSV_FILENAME_TEMPLATE.format(
            row.PID, row.create_time
        )
        metrics = pd.read_csv(metrics_csv_filename, parse_dates=["Time"])

        # Focus on groups based on the core where it was working
        # grouped = metrics.groupby(["core_num"])
        # print(metrics.head())
        full_stats.append(metrics)

    pids["command"] = main_commands
    pids["command_label"] = command_labels
    pids["full_command"] = full_command
    pids["full_stats"] = pd.array(full_stats, dtype="object", copy=False)
    pids["subtree_root"] = subtree_root

    return reference_pid, pids, num_cpu_cores, sampling_period_seconds


def timedelta_full_formatter(td: "pd.Timedelta") -> "str":
    return str(td)


def timedelta_noday_formatter(td: "pd.Timedelta") -> "str":
    if td.components.days > 0:
        return timedelta_full_formatter(td)

    if td.components.milliseconds > 0:
        return "{0:02d}:{1:02d}:{2:02d}.{3:03d}".format(
            td.components.hours,
            td.components.minutes,
            td.components.seconds,
            td.components.milliseconds,
        )
    else:
        return "{0:02d}:{1:02d}:{2:02d}".format(
            td.components.hours, td.components.minutes, td.components.seconds
        )
