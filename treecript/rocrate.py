#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0-or-later
# treecript, a process tree metrics gatherer.
# Copyright (C) 2026 Barcelona Supercomputing Center, José M. Fernández
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

import argparse
import datetime
import logging
import pathlib

from typing import (
    cast,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Final,
        Mapping,
        Optional,
        Sequence,
        Set,
    )

    import pandas.core.series

from pandas import isna as pandas_isna

import rocrate.model.creativework
import rocrate.model.contextentity
import rocrate.rocrate

from .parser import (
    metrics_parser,
)

WRROC_CONTEXT: "Final[str]" = "https://w3id.org/ro/terms/workflow-run/context"
SCHEMA_ORG_NAMESPACE: "Final[str]" = "http://schema.org/"

logger = logging.getLogger(__name__)

TREECRIPT_SKIPPABLE = set(["Time", "PID"])

# UN/CEFACT Common Codes
# See https://unece.org/sites/default/files/2023-10/rec20_Rev17e-2021.xlsx
# Obtained from https://unece.org/trade/uncefact/cl-recommendations
# at Rec 20 – Codes for Units of Measure Used in International Trade dropdown
TREECRIPT_UNITS_MAPPING_OLD = {
    # "PID"
    "Virt": "AD",  # code for byte
    "Res": "AD",
    "CPU": "P1",  # code for percent
    "Memory": "P1",
    # "TCP Connections"
    # "Thread Count"
    "User": "P1",
    "System": "P1",
    "Children_User": "P1",
    "Children_System": "P1",
    "IO": "P1",
    "uss": "AD",
    "swap": "AD",
    # "processor_num"
    # "core_num"
    # "cpu_num"
    # "cpu_ids"
    # "process_status"
    # "read_count"
    # "write_count"
    "read_bytes": "AD",
    "write_bytes": "AD",
    "read_chars": "AD",
    "write_chars": "AD",
}

TREECRIPT_UNITS_MAPPING: "Mapping[str, Mapping[str, Optional[str]]]" = {
    "PID": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#pid",
        "unitCode": None,
        "additionalType": "Integer",
    },
    "PPID": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#pid",
        "unitCode": None,
        "additionalType": "Integer",
    },
    "Virt": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#virt",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "Res": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#res",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "CPU": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#cpu",
        "unitCode": "http://qudt.org/vocab/unit/PERCENT",
        "additionalType": "Float",
    },
    "Memory": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#memory",
        "unitCode": "http://qudt.org/vocab/unit/PERCENT",
        "additionalType": "Float",
    },
    "TCP Connections": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#tcp_connections",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "Thread Count": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#thread_count",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "User": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#user",
        "unitCode": "http://qudt.org/vocab/unit/SEC",
        "additionalType": "Float",
    },
    "System": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#system",
        "unitCode": "http://qudt.org/vocab/unit/SEC",
        "additionalType": "Float",
    },
    "Children_User": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#children_user",
        "unitCode": "http://qudt.org/vocab/unit/SEC",
        "additionalType": "Float",
    },
    "Children_System": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#children_system",
        "unitCode": "http://qudt.org/vocab/unit/SEC",
        "additionalType": "Float",
    },
    "IO": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#io",
        "unitCode": "http://qudt.org/vocab/unit/SEC",
        "additionalType": "Float",
    },
    "uss": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#uss",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "swap": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#swap",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "processor_num": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#processor_num",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "core_num": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#core_num",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "cpu_num": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#cpu_num",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "processor_ids": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#processor_ids",
        "unitCode": None,
        "additionalType": "String",
    },
    "core_ids": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#core_ids",
        "unitCode": None,
        "additionalType": "String",
    },
    "cpu_ids": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#cpu_ids",
        "unitCode": None,
        "additionalType": "String",
    },
    "process_status": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#process_status",
        "unitCode": None,
        "additionalType": "String",
    },
    "read_count": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#read_count",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "write_count": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#write_count",
        "unitCode": "http://qudt.org/vocab/unit/CountingUnit",
        "additionalType": "Integer",
    },
    "read_bytes": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#read_bytes",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "write_bytes": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#write_bytes",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "read_chars": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#read_chars",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
    "write_chars": {
        "propertyID": "https://w3id.org/ro/terms/treecript-metrics#write_chars",
        "unitCode": "http://qudt.org/vocab/unit/BYTE",
        "additionalType": "Integer",
    },
}


def create_property_value(
    wrroc: "rocrate.rocrate.ROCrate", name: "str", value: "Any"
) -> "rocrate.model.contextentity.ContextEntity":
    metric = rocrate.model.contextentity.ContextEntity(
        wrroc,
        None,
        properties={
            "@type": "PropertyValue",
            "name": name,
            "value": str(value),
        },
    )
    wrroc.add(metric)

    mapping = TREECRIPT_UNITS_MAPPING.get(name)
    if mapping is not None:
        property_id = mapping["propertyID"]
        metric.append_to("propertyID", property_id, compact=True)

        unit_code = mapping.get("unitCode")
        if unit_code is not None:
            metric.append_to("unitCode", unit_code, compact=True)

        additional_type = mapping.get("additionalType")
        if additional_type is not None:
            metric.append_to("additionalType", additional_type, compact=True)

    return metric


def create_action(
    wrroc: "rocrate.rocrate.ROCrate",
    pid_row: "pandas.core.series.Series[Any]",
    skippable_metric: "Set[str]" = TREECRIPT_SKIPPABLE,
) -> "rocrate.model.contextentity.ContextEntity":
    start_action = (
        datetime.datetime.fromtimestamp(pid_row.create_time).astimezone().isoformat()
    )
    action = rocrate.model.contextentity.ContextEntity(
        wrroc,
        "#" + pid_row.node,
        properties={
            "@type": "CreateAction",
            "name": pid_row.PID,
            "description": " ".join(pid_row.full_command),
            "startTime": start_action,
            # "endTime": "",
        },
    )
    wrroc.add(action)

    pid_metric = create_property_value(wrroc, "PID", pid_row.PID)
    ppid_metric = create_property_value(wrroc, "PPID", pid_row.PPID)
    action.append_to("resourceUsage", [pid_metric, ppid_metric], compact=True)

    organize_action = rocrate.model.contextentity.ContextEntity(
        wrroc,
        "#" + pid_row.node + "_organize",
        properties={
            "@type": "OrganizeAction",
            "name": "Run of " + " ".join(pid_row.full_command),
            "startTime": start_action,
        },
    )

    wrroc.add(organize_action)
    organize_action.append_to("result", action, compact=True)

    assert len(pid_row.full_command) > 0
    software_application = rocrate.model.contextentity.ContextEntity(
        wrroc,
        "#" + pid_row.node + "_software_application",
        properties={
            "@type": "SoftwareApplication",
            "name": pid_row.full_command[0],
        },
    )
    wrroc.add(software_application)
    organize_action.append_to("instrument", software_application, compact=True)
    action.append_to("instrument", software_application, compact=True)

    # Try registering this control action with its parent (if exists)
    control_action = rocrate.model.contextentity.ContextEntity(
        wrroc,
        "#" + pid_row.node + "_control_action",
        properties={
            "@type": "ControlAction",
            "name": "Orchestrate " + " ".join(pid_row.full_command),
        },
    )
    wrroc.add(control_action)
    control_action.append_to("object", action, compact=True)

    howto_step = rocrate.model.contextentity.ContextEntity(
        wrroc,
        "#" + pid_row.node + "_howto_step",
        properties={
            "@type": "HowToStep",
        },
    )
    wrroc.add(howto_step)
    howto_step.append_to("workExample", software_application, compact=True)
    control_action.append_to("instrument", howto_step, compact=True)

    if not pandas_isna(pid_row.parent):
        parent_organize_action = cast(
            "Optional[rocrate.model.contextentity.ContextEntity]",
            wrroc.dereference("#" + pid_row.parent + "_organize"),
        )
        if parent_organize_action is not None:
            parent_organize_action.append_to("object", control_action, compact=True)

    action_series = rocrate.model.contextentity.ContextEntity(
        wrroc,
        "#series_" + pid_row.node,
        properties={
            "@type": "EventSeries",
            "about": action,
            "startDate": start_action,
        },
    )
    wrroc.add(action_series)
    action.append_to("subjectOf", action_series, compact=True)

    for index, row in pid_row.full_stats.iterrows():
        i_event = rocrate.model.contextentity.ContextEntity(
            wrroc,
            f"#event_{index}_{pid_row.node}",
            properties={
                "@type": ["InstantaneousEvent", "Event"],
                "superEvent": action_series,
                "source": action,
                "timestamp": row.Time.to_pydatetime().astimezone().isoformat(),
            },
        )
        wrroc.add(i_event)
        action_series.append_to("subEvent", i_event, compact=True)

        # Now, the metrics
        metrics = []
        for name, value in row.items():
            if name in skippable_metric:
                continue

            metric = create_property_value(wrroc, name, value)
            metrics.append(metric)

        if len(metrics) > 0:
            i_event.append_to("data", metrics, compact=True)

    return action


def describe_metrics_in_wrroc(
    wrroc: "rocrate.rocrate.ROCrate", series_dir: "pathlib.Path"
) -> "None":
    reference_pid, pids, num_cpu_cores, sampling_period_seconds = metrics_parser(
        series_dir
    )

    for pid_tuple in pids.iterrows():
        pid_row = pid_tuple[1]

        action = create_action(wrroc, pid_row)
        # This is the root
        if pid_row.PID == reference_pid:
            wrroc.root_dataset.append_to("mentions", action, compact=True)


def bundle_as_wrroc(
    series_dirs: "Sequence[pathlib.Path]",
    wrroc_path: "pathlib.Path",
    save_as_directory: "bool" = False,
) -> "pathlib.Path":
    """
    This method takes as input one directory full of gathered metrics
    about a process tree, and it generates a WRROC describing it properly.
    """

    # Next calls are setting up the pre-requisites for a WRROC
    wrroc = rocrate.rocrate.ROCrate(version="1.1")
    wrroc.metadata.extra_contexts.append(WRROC_CONTEXT)

    # And the term needed by this WRROC metrics generator
    wrroc.metadata.extra_terms.update(
        {
            # See https://schema.org/InstantaneousEvent
            "InstantaneousEvent": SCHEMA_ORG_NAMESPACE + "InstantaneousEvent",
        }
    )

    wrroc_profiles = [
        rocrate.model.creativework.CreativeWork(
            wrroc,
            identifier="https://w3id.org/ro/wfrun/process/0.5",
            properties={"name": "Process Run Crate", "version": "0.5"},
        ),
        rocrate.model.creativework.CreativeWork(
            wrroc,
            identifier="https://w3id.org/ro/wfrun/workflow/0.5",
            properties={"name": "Workflow Run Crate", "version": "0.5"},
        ),
        rocrate.model.creativework.CreativeWork(
            wrroc,
            identifier="https://w3id.org/ro/wfrun/provenance/0.5",
            properties={"name": "Provenance Run Crate", "version": "0.5"},
        ),
    ]

    wrroc.add(*wrroc_profiles)
    wrroc.root_dataset.append_to("conformsTo", wrroc_profiles, compact=True)

    wc_profile = rocrate.model.creativework.CreativeWork(
        wrroc,
        identifier="https://w3id.org/workflowhub/workflow-ro-crate/1.0",
        properties={"name": "Workflow RO-Crate", "version": "1.0"},
    )
    wrroc.add(wc_profile)
    wrroc.root_dataset.append_to("conformsTo", wc_profile, compact=True)
    wrroc.metadata.append_to("conformsTo", wc_profile, compact=True)

    # Now, it is time to populate the WRROC
    for series_dir in series_dirs:
        describe_metrics_in_wrroc(wrroc, series_dir)

    # Last, save it!
    if save_as_directory:
        wrroc.write(wrroc_path)
    else:
        wrroc.write_zip(wrroc_path)

    return wrroc_path


def main() -> "None":
    parser = argparse.ArgumentParser()

    meg = parser.add_mutually_exclusive_group()
    meg.add_argument(
        "-q",
        dest="logging_level",
        const=logging.ERROR,
        help="Be quiet, print only the consumption",
        action="store_const",
    )
    meg.add_argument(
        "-d",
        dest="logging_level",
        const=logging.DEBUG,
        help="Switch logging to Be quiet, print only the consumption",
        action="store_const",
    )

    parser.add_argument(
        "--as-directory",
        dest="as_directory",
        default=False,
        help="Store the RO-Crate as a directory instead of a zip archive",
        action="store_true",
    )

    parser.add_argument(
        "rocrate_dest",
        help="Path to the RO-Crate",
        type=pathlib.Path,
    )
    parser.add_argument(
        "series_dirs",
        nargs="+",
        help="Series directory to be described within the WRROC",
        type=pathlib.Path,
    )

    args = parser.parse_args()

    logging_level = (
        args.logging_level if args.logging_level is not None else logging.WARNING
    )

    logging.basicConfig(level=logging_level)

    series_dirs = list(map(pathlib.Path, args.series_dirs))

    bundle_as_wrroc(series_dirs, args.rocrate_dest, save_as_directory=args.as_directory)


if __name__ == "__main__":
    main()
