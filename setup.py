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

import re
import os
import sys
import setuptools

from typing import (
    cast,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        Final,
        MutableMapping,
        MutableSequence,
        Sequence,
    )

# In this way, we are sure we are getting
# the installer's version of the library
# not the system's one
setupDir = os.path.dirname(__file__)
sys.path.insert(0, setupDir)

from treecript import __version__ as epmc_version
from treecript import __author__ as epmc_author
from treecript import __license__ as epmc_license

EGG_PAT = re.compile(r"#[^#]*egg=([^=&]+)")
OTHER_REQ_PAT = re.compile(r"^-r\s+(.+)")
REQ_SECT_PAT = re.compile(r"^requirements-([^.]+)\.txt$")

CORE_REQUIREMENTS: "Final[str]" = "core"


def populate_extra_requirements(
    requirements_path: "str", section: "str" = CORE_REQUIREMENTS
) -> "MutableMapping[str, Sequence[str]]":
    extra_requirements: "MutableMapping[str, MutableSequence[str]]" = {}
    if os.path.exists(requirements_path):
        # Be sure the path is an absolute one
        if not os.path.isabs(requirements_path):
            requirements_path = os.path.abspath(requirements_path)

        with open(requirements_path, mode="r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                rm = OTHER_REQ_PAT.search(line)
                if rm is None:
                    print(f"R {line}")
                    m = EGG_PAT.search(line)
                    extra_requirements.setdefault(section, []).append(
                        line if m is None else m.group(1)
                    )
                else:
                    # This is needed for cases like -r
                    other_requirements_path = os.path.realpath(
                        os.path.join(os.path.dirname(requirements_path), rm.group(1))
                    )
                    other_requirements_basename = os.path.basename(
                        other_requirements_path
                    )

                    nested_section = section
                    rsmatch = REQ_SECT_PAT.search(other_requirements_basename)
                    if rsmatch is not None:
                        nested_section = rsmatch.group(1)

                    nested_extra_requirements = populate_extra_requirements(
                        other_requirements_path, section=nested_section
                    )
                    for nested_sect, nested_deps in nested_extra_requirements.items():
                        extra_requirements.setdefault(nested_sect, []).extend(
                            nested_deps
                        )

    return cast("MutableMapping[str, Sequence[str]]", extra_requirements)


# Populating the long description
readme_path = os.path.join(setupDir, "README.md")
with open(readme_path, "r") as fh:
    long_description = fh.read()

# Populating the install requirements
requirements_path = os.path.join(setupDir, "installation", "requirements.txt")
extra_requirements = populate_extra_requirements(requirements_path)
requirements = extra_requirements.pop(CORE_REQUIREMENTS, [])

setuptools.setup(
    name="treecript",
    version=epmc_version,
    author=epmc_author,
    author_email="jose.m.fernandez@bsc.es",
    license=epmc_license,
    description="Process tree metrics gatherer and digester",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inab/treecript",
    project_urls={"Bug Tracker": "https://github.com/inab/treecript/issues"},
    packages=setuptools.find_packages(),
    package_data={
        "treecript": [
            "py.typed",
        ]
    },
    scripts=[
        "cpuinfo-tdp-finder.py",
        "execution-metrics-collector.py",
        "process-metrics-collector.py",
        "metrics-aggregator.py",
        "modelname-tdp-finder.py",
        "plotGraph.py",
        "tdp-finder.py",
        "legacy/execution-metrics-collector.sh",
        "legacy/plotGraph.sh",
        "legacy/plot-metrics.sh",
    ],
    entry_points={
        "console_scripts": [
            "execution-metrics-collector = treecript.collector:main__commandline",
            "process-metrics-collector = treecript.collector:main",
            "cpuinfo-tdp-finder = treecript.tdp_finder:main_cpuinfo_tdp_finder [analytics]",
            "modelname-tdp-finder = treecript.tdp_finder:main_modelname_tdp_finder [analytics]",
            "tdp-finder = treecript.tdp_finder:main_tdp_finder [analytics]",
            "metrics-aggregator = treecript.aggregator:main [analytics]",
            "plotGraph = treecript.plot_graph:main [analytics]",
        ],
    },
    install_requires=requirements,
    extras_require=extra_requirements,  # type: ignore[arg-type]
    # See https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
