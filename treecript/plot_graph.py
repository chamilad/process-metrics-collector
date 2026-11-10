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

import datetime
import pathlib
import sys

from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        List,
        Optional,
    )

    from matplotlib.typing import RcKeyType

import matplotlib
from matplotlib.colors import TABLEAU_COLORS
import matplotlib.pyplot as plt

import pandas as pd

from .parser import (
    metrics_parser,
)


# Borrowed from https://stackoverflow.com/a/31631711
def humanbytes(B: "float") -> "str":
    """Return the given bytes as a human friendly KB, MB, GB, or TB string."""
    B = float(B)
    KB = float(1024)
    MB = float(KB**2)  # 1,048,576
    GB = float(KB**3)  # 1,073,741,824
    TB = float(KB**4)  # 1,099,511,627,776

    if B < KB:
        return "{0} {1}".format(B, "Bytes" if 0 == B > 1 else "Byte")
    elif KB <= B < MB:
        return "{0:.2f} KB".format(B / KB)
    elif MB <= B < GB:
        return "{0:.2f} MB".format(B / MB)
    elif GB <= B < TB:
        return "{0:.2f} GB".format(B / GB)
    # elif TB <= B:
    return "{0:.2f} TB".format(B / TB)


def cpu_and_memory_graph(
    pids: "pd.DataFrame",
    outputs_dir: "pathlib.Path",
    width: "float" = 16.6,
    height: "float" = 11.7,
    dpi: "int" = 300,
    font_size: "float" = 10,
) -> "None":
    rc_context: "dict[RcKeyType, Any]" = {
        "font.size": font_size * 1.7,  # controls default text sizes
        "axes.titlesize": font_size * 1.5,  # fontsize of the axes title
        "axes.labelsize": font_size * 1.5,  # fontsize of the x and y labels
        "xtick.labelsize": font_size * 1.2,  # fontsize of the tick labels
        "ytick.labelsize": font_size * 1.2,  # fontsize of the tick labels
        "legend.fontsize": font_size,  # legend fontsize
        "figure.titlesize": font_size * 2,  # fontsize of the figure title
    }

    for pid_tuple in pids.iterrows():
        pid_row = pid_tuple[1]
        with plt.rc_context(rc_context):
            fig, ax = plt.subplots(figsize=(width, height), dpi=dpi, tight_layout=True)

            title = f"""\
% CPU and Memory Usage
{pid_row.command}
{pid_row.node}
Generated on {datetime.datetime.now().astimezone().isoformat()}\
"""
            pid_row.full_stats.plot.line(
                x="RelTime",
                y="CPU",
                title=title,
                ax=ax,
            )
            pid_row.full_stats.plot.line(
                x="RelTime",
                y="uss",
                secondary_y=True,
                ax=ax,
            )
            pid_row.full_stats.plot.line(
                x="RelTime",
                y="swap",
                secondary_y=True,
                ax=ax,
            )

            # ax.xaxis.set_major_formatter(
            #    lambda x, pos: timedelta_noday_formatter(pd.Timedelta(x))
            # )
            ax.set_xlabel("Relative time")
            ax.set_ylabel("% CPU")
            ax.right_ax.set_ylabel("Memory")  # type: ignore[attr-defined]
            ax.right_ax.yaxis.set_major_formatter(  # type: ignore[attr-defined]
                lambda x, pos: humanbytes(x)
            )

            #            ax.yaxis.axes.set_xlabel("Relative time")

            the_pid = pid_row.node

            matplotlib.use("pdf")
            fig.savefig(outputs_dir / f"cpu_and_memory_graph-process_{the_pid}.pdf")

            matplotlib.use("svg")
            fig.savefig(outputs_dir / f"cpu_and_memory_graph-process_{the_pid}.svg")

            matplotlib.use("agg")
            fig.savefig(outputs_dir / f"cpu_and_memory_graph-process_{the_pid}.png")

        plt.close(fig)


def cpu_and_io_graph(
    pids: "pd.DataFrame",
    outputs_dir: "pathlib.Path",
    width: "float" = 16.6,
    height: "float" = 11.7,
    dpi: "int" = 300,
    font_size: "float" = 10,
) -> "None":
    rc_context: "dict[RcKeyType, Any]" = {
        "font.size": font_size * 1.7,  # controls default text sizes
        "axes.titlesize": font_size * 1.5,  # fontsize of the axes title
        "axes.labelsize": font_size * 1.5,  # fontsize of the x and y labels
        "xtick.labelsize": font_size * 1.2,  # fontsize of the tick labels
        "ytick.labelsize": font_size * 1.2,  # fontsize of the tick labels
        "legend.fontsize": font_size,  # legend fontsize
        "figure.titlesize": font_size * 2,  # fontsize of the figure title
    }

    for pid_tuple in pids.iterrows():
        pid_row = pid_tuple[1]
        with plt.rc_context(rc_context):
            fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
            ax3 = ax.twinx()
            rspine = ax3.spines["right"]
            rspine.set_position(("axes", 1.15))
            ax3.set_frame_on(True)
            ax3.patch.set_visible(False)
            fig.subplots_adjust(right=0.7)

            colors = list(TABLEAU_COLORS.values())
            title = f"""\
% CPU and Memory Usage
{pid_row.command}
{pid_row.node}
Generated on {datetime.datetime.now().astimezone().isoformat()}\
"""
            pid_row.full_stats.plot.line(
                x="RelTime",
                y="CPU",
                color=colors[0],
                title=title,
                ax=ax,
            ).legend(bbox_to_anchor=(1, 1))
            pid_row.full_stats.plot.line(
                x="RelTime",
                y="uss",
                color=colors[1],
                secondary_y=True,
                ax=ax,
            )

            pid_row.full_stats.plot.line(
                x="RelTime",
                y="read_count",
                color=colors[2],
                style=":",
                ax=ax3,
            )
            pid_row.full_stats.plot.line(
                x="RelTime",
                y="write_count",
                color=colors[3],
                style="--",
                ax=ax3,
            ).legend(bbox_to_anchor=(1, 1))

            # ax.xaxis.set_major_formatter(
            #    lambda x, pos: timedelta_noday_formatter(pd.Timedelta(x))
            # )
            ax.set_xlabel("Relative time")
            ax.set_ylabel("% CPU")
            ax.right_ax.set_ylabel("Memory")  # type: ignore[attr-defined]
            ax.right_ax.yaxis.set_major_formatter(  # type: ignore[attr-defined]
                lambda x, pos: humanbytes(x)
            )
            ax3.set_ylabel("# I/O ops")

            #            ax.yaxis.axes.set_xlabel("Relative time")

            the_pid = pid_row.node

            matplotlib.use("pdf")
            fig.savefig(outputs_dir / f"cpu_and_io_graph-process_{the_pid}.pdf")

            matplotlib.use("svg")
            fig.savefig(outputs_dir / f"cpu_and_io_graph-process_{the_pid}.svg")

            matplotlib.use("agg")
            fig.savefig(outputs_dir / f"cpu_and_io_graph-process_{the_pid}.png")

        plt.close(fig)


def plot_graphs(
    series_dir: "pathlib.Path",
    outputs_dir: "pathlib.Path",
    group_by_process_name: "Optional[str]" = None,
) -> "None":
    reference_pid, pids, num_cpu_cores, sampling_period_seconds = metrics_parser(
        series_dir,
        group_by_process_name=group_by_process_name,
    )

    # Make sure indexes pair with number of rows
    # See https://stackoverflow.com/a/16476974
    pids = pids.reset_index()

    # sampling_period_milliseconds = int(round(sampling_period_seconds * 1000.0))
    # sampling_period_td = pd.Timedelta(sampling_period_milliseconds, "ms")

    # First pass
    node_first: "List[pd.Timestamp]" = []
    for pid_tuple in pids.iterrows():
        pid_row = pid_tuple[1]
        metrics = pid_row.full_stats
        first_sample = metrics["Time"].min()
        node_first.append(first_sample)

    node_first.sort()

    start_point = node_first[0]

    # Generating the RelStart
    for pid_tuple in pids.iterrows():
        pid_row = pid_tuple[1]
        pid_row.full_stats["RelTime"] = pid_row.full_stats["Time"] - start_point

    outputs_dir.mkdir(parents=True, exist_ok=True)
    # Now, let's reproduce the very same charts generated using gnuplot
    # through plotGraph.sh
    cpu_and_memory_graph(pids, outputs_dir)
    cpu_and_io_graph(pids, outputs_dir)


def main() -> "None":
    if len(sys.argv) >= 3:
        group_by_process_name = sys.argv[3] if len(sys.argv) >= 4 else None
        plot_graphs(
            pathlib.Path(sys.argv[1]),
            pathlib.Path(sys.argv[2]),
            group_by_process_name=group_by_process_name,
        )
    else:
        print(
            f"Usage: {sys.argv[0]} {{series_dir}} {{outputs_dir}} [group_by_program_name]",
            file=sys.stderr,
        )
        sys.exit(1)
