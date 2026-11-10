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

import argparse
import json
import logging
import pathlib
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Final,
        List,
        MutableSequence,
        Sequence,
        Set,
        Tuple,
        Union,
    )

    from .common import (
        CPUInfo,
    )

from .common import (
    CPU_DETAILS_FILENAME,
    parse_cpuinfo,
)

from .tdp_sources import (
    CRAWLERS_TDP_COLUMN,
    HONORED_KEY_COLUMNS_CRAWLERS,
)

import pandas as pd


HONORED_KEY_COLUMNS_CPU_SPEC_DATASET: "Final[Sequence[str]]" = (
    "ProcessorNumber",
    "Processor Number",
    "Name",
    "CpuName",
)

HONORED_KEY_COLUMNS: "Final[Sequence[str]]" = (
    *HONORED_KEY_COLUMNS_CPU_SPEC_DATASET,
    *HONORED_KEY_COLUMNS_CRAWLERS,
)

logger = logging.getLogger(__name__)


def _tdp_finder_from_model_name(
    model_name: "str",
    key_column: "str",
    cpus_df: "pd.DataFrame",
    processors_file: "pathlib.Path",
) -> "Tuple[str, str, float, pathlib.Path]":
    if key_column not in cpus_df:
        errmsg = f"Unable to find a valid processor identification column in file {processors_file.as_posix()}"
        logger.error(errmsg)
        raise KeyError(errmsg)
    elif (
        key_column in HONORED_KEY_COLUMNS_CRAWLERS
        and CRAWLERS_TDP_COLUMN not in cpus_df
    ):
        errmsg = f"Unable to find a valid processor TDP column in file {processors_file.as_posix()}"
        logger.error(errmsg)
        raise KeyError(errmsg)

    filtered_cpus = cpus_df[cpus_df[key_column].apply(lambda pn: str(pn) in model_name)]

    if len(filtered_cpus) == 0:
        errmsg = f"Unable to match a valid processor row for {model_name} in file {processors_file.as_posix()}"
        logger.warning(errmsg)
        raise LookupError(errmsg)

    matches: "List[Tuple[str, Union[str, float, int]]]" = []
    tried_match = False
    if key_column in HONORED_KEY_COLUMNS_CRAWLERS:
        column = filtered_cpus[CRAWLERS_TDP_COLUMN]
        if not column.hasnans:
            putative_tdp_val = column.values[0]
            if isinstance(putative_tdp_val, (str, float, int)):
                tried_match = True
                matches.append((CRAWLERS_TDP_COLUMN, putative_tdp_val))
    else:
        for column_name, column in filtered_cpus.items():
            if not column.hasnans:
                putative_tdp_str = column.values[0]
                if isinstance(putative_tdp_str, str):
                    tried_match = True
                    matched = re.search(
                        r"^(?:[0-9]+(?:\.[0-9]+])?-)?([0-9]+(?:\.[0-9]+])?) W",
                        putative_tdp_str,
                    )
                    if matched:
                        matches.append((str(column_name), matched.group(1)))

    if len(matches) == 0:
        if tried_match:
            submsg = "found model description but not the consumption"
        else:
            submsg = "no match on model description"
        errmsg = f"Unable to find processor package consumption values for {model_name} in file {processors_file.as_posix()} ({submsg})"
        logger.warning(errmsg)
        raise ValueError(errmsg)
    elif len(matches) > 1:
        # Now, sort by consumption
        matches.sort(key=lambda t: t[1], reverse=True)

    return (model_name, matches[0][0], float(matches[0][1]), processors_file)


class TDPFinderException(Exception):
    pass


def tdp_finder_from_model_name(
    model_name: "str", processors_files: "Sequence[pathlib.Path]"
) -> "Tuple[str, str, float, pathlib.Path]":
    errors = []
    notfound = []
    for processors_file in processors_files:
        # low_memory is needed to avoid a warning in some CSV files with mixed data
        cpus = pd.read_csv(processors_file, low_memory=False)

        for key_column in HONORED_KEY_COLUMNS:
            if key_column in cpus:
                break
        else:
            errors.append(
                f"Unable to find a valid processor identification column in file {processors_file.as_posix()}"
            )
            continue

        try:
            return _tdp_finder_from_model_name(
                model_name, key_column, cpus, processors_file
            )
        except LookupError:
            # We are recovering for this case, where
            errmsg = f"Nothing found for {model_name} under {key_column} in {processors_file.as_posix()}"
            logger.debug(errmsg)
            notfound.append(errmsg)

    if len(errors) > 0 or len(notfound) > 0:
        for error in (*errors, *notfound):
            logger.error(error)

    raise TDPFinderException(
        f"Unmatched {model_name} over datasheet processor files (see logs for detailed messages)"
    )


def tdp_finder_from_cpuinfo(
    cpu_details: "Sequence[CPUInfo]", processors_files: "Sequence[pathlib.Path]"
) -> "Sequence[Tuple[str, str, float, pathlib.Path]]":
    # First, account for the number of different model names
    unique_model_names: "Set[str]" = set()
    for cpu_details_cpu in cpu_details:
        model_name = cpu_details_cpu["model name"]
        unique_model_names.add(model_name)

    errors = []
    found_tdp: "MutableSequence[Tuple[str, str, float, pathlib.Path]]" = []
    seen_model_names: "Set[str]" = set()
    for processors_file in processors_files:
        # low_memory is needed to avoid a warning in some CSV files with mixed data
        cpus = pd.read_csv(processors_file, low_memory=False)
        # print(f"COLUMNS {processors_file.as_posix()} {list(cpus.columns)}")

        for key_column in HONORED_KEY_COLUMNS:
            if key_column in cpus:
                break
        else:
            errors.append(
                f"Unable to find a valid processor identification column in file {processors_file.as_posix()}"
            )
            continue

        for model_name in unique_model_names:
            if model_name not in seen_model_names:
                try:
                    found_tdp.append(
                        _tdp_finder_from_model_name(
                            model_name, key_column, cpus, processors_file
                        )
                    )
                    seen_model_names.add(model_name)
                except LookupError:
                    # We are recovering for this case, where
                    logger.debug(
                        f"Nothing found for {model_name} under {key_column} in {processors_file.as_posix()}"
                    )

        # Once all matches are found, answer
        if len(found_tdp) == len(unique_model_names):
            break

    if len(found_tdp) == 0 and len(errors) > 0:
        for error in errors:
            logger.error(error)

        raise TDPFinderException()

    return found_tdp


class TDPFinderPathException(TDPFinderException):
    pass


def tdp_finder_from_series(
    series_dir: "pathlib.Path", processors_files: "Sequence[pathlib.Path]"
) -> "Sequence[Tuple[str, str, float, pathlib.Path]]":
    if not series_dir.is_dir():
        errmsg = f"Path {series_dir.as_posix()} is not a directory"
        logger.error(errmsg)
        raise TDPFinderPathException(errmsg)

    cpu_details_filename = series_dir / CPU_DETAILS_FILENAME
    if not cpu_details_filename.is_file():
        errmsg = f"Path {cpu_details_filename.as_posix()} is not a filename"
        logger.error(errmsg)
        raise TDPFinderPathException(errmsg)

    with cpu_details_filename.open(mode="r", encoding="utf-8") as cF:
        cpu_details = json.load(cF)

    return tdp_finder_from_cpuinfo(cpu_details, processors_files)


def tdp_finder_from_raw(
    cpuinfo_file: "pathlib.Path", processors_files: "Sequence[pathlib.Path]"
) -> "Sequence[Tuple[str, str, float, pathlib.Path]]":
    if not cpuinfo_file.is_file():
        errmsg = f"Path {cpuinfo_file.as_posix()} is not a file"
        logger.error(errmsg)
        raise TDPFinderPathException(errmsg)

    cpu_hash, processor2corecpu = parse_cpuinfo(cpuinfo_file.as_posix())

    return tdp_finder_from_cpuinfo(list(cpu_hash.values()), processors_files)


def main_tdp_finder() -> "None":
    par_parser = argparse.ArgumentParser()

    meg = par_parser.add_mutually_exclusive_group()
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

    par_parser.add_argument(
        "series_dir",
        help="Directory of the gathered metrics timeline, where the CPU details were recorded",
    )
    par_parser.add_argument(
        "cpu_database_files",
        nargs="+",
        help="The CSV files where the list of CPUs are available, along with their consumptions",
    )

    args = par_parser.parse_args()

    logging_level = (
        args.logging_level if args.logging_level is not None else logging.WARNING
    )

    logging.basicConfig(level=logging_level)

    for model_name, tdp_column, tdp_in_w, processors_file in tdp_finder_from_series(
        pathlib.Path(args.series_dir), list(map(pathlib.Path, args.cpu_database_files))
    ):
        if logging_level < logging.ERROR:
            print(
                f"Model [{model_name}] => TDP [{tdp_column}] => {tdp_in_w} W => File {processors_file.as_posix()}"
            )
        else:
            print(str(tdp_in_w))


def main_cpuinfo_tdp_finder() -> "None":
    par_parser = argparse.ArgumentParser()

    meg = par_parser.add_mutually_exclusive_group()
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

    par_parser.add_argument(
        "cpuinfo_file",
        help="CPU details provided by Linux kernel, usually available at /proc/cpuinfo",
    )
    par_parser.add_argument(
        "cpu_database_files",
        nargs="+",
        help="The CSV files where the list of CPUs are available, along with their consumptions",
    )

    args = par_parser.parse_args()

    logging_level = (
        args.logging_level if args.logging_level is not None else logging.WARNING
    )

    logging.basicConfig(level=logging_level)

    for model_name, tdp_column, tdp_in_w, processors_file in tdp_finder_from_raw(
        pathlib.Path(args.cpuinfo_file),
        list(map(pathlib.Path, args.cpu_database_files)),
    ):
        if logging_level < logging.ERROR:
            print(
                f"Model [{model_name}] => TDP [{tdp_column}] => {tdp_in_w} W => File {processors_file.as_posix()}"
            )
        else:
            print(str(tdp_in_w))


def main_modelname_tdp_finder() -> "None":
    par_parser = argparse.ArgumentParser()

    meg = par_parser.add_mutually_exclusive_group()
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

    par_parser.add_argument(
        "model_string",
        help="Processor model string to be searched",
    )
    par_parser.add_argument(
        "cpu_database_files",
        nargs="+",
        help="The CSV files where the list of CPUs are available, along with their consumptions",
    )

    args = par_parser.parse_args()

    logging_level = (
        args.logging_level if args.logging_level is not None else logging.WARNING
    )

    logging.basicConfig(level=logging_level)

    model_name, tdp_column, tdp_in_w, processors_file = tdp_finder_from_model_name(
        args.model_string, list(map(pathlib.Path, args.cpu_database_files))
    )
    if logging_level < logging.ERROR:
        print(
            f"Model [{model_name}] => TDP [{tdp_column}] => {tdp_in_w} W => File {processors_file.as_posix()}"
        )
    else:
        print(str(tdp_in_w))
