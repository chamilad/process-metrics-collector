import click
from typing import (
    Any,
    Optional,
    Sequence,
    Set,
)

from .model.computerlanguage import LANG_MAP as LANG_MAP
from .model.contextentity import add_hash as add_hash
from .model.softwareapplication import APP_MAP as APP_MAP
from .model.testservice import SERVICE_MAP as SERVICE_MAP
from .rocrate import ROCrate as ROCrate

LANG_CHOICES: Sequence[str]
SERVICE_CHOICES: Sequence[str]
ENGINE_CHOICES: Sequence[str]

class CSVParamType(click.ParamType[str]):  # type: ignore[type-arg]
    name: str
    def convert(self, value: Any, param: Any, ctx: Any) -> Any: ...

CSV: CSVParamType
OPTION_CRATE_PATH: Any

def cli() -> None: ...
def init(
    crate_dir: str, gen_preview: bool, exclude: Optional[Sequence[str] | Set[str]]
) -> None: ...
def add() -> None: ...
def workflow(crate_dir: str, path: str, language: str) -> None: ...
def suite(
    crate_dir: str,
    identifier: Optional[str],
    name: Optional[str],
    main_entity: Optional[str],
) -> None: ...
def instance(
    crate_dir: str,
    suite: Optional[str],
    url: str,
    resource: str,
    service: str,
    identifier: Optional[str],
    name: Optional[str],
) -> None: ...
def definition(
    crate_dir: str,
    suite: Optional[str],
    path: str,
    engine: str,
    engine_version: Optional[str],
) -> None: ...
def write_zip(crate_dir: str, dst: str) -> None: ...
