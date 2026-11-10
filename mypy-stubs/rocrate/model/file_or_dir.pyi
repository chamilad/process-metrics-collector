from pathlib import Path
from typing import (
    Any,
    Mapping,
    Optional,
)

from ..utils import is_url as is_url
from .data_entity import DataEntity as DataEntity
from ..rocrate import ROCrate

class FileOrDir(DataEntity):
    fetch_remote: bool
    validate_url: bool
    source: Optional[str | Path]
    def __init__(
        self,
        crate: ROCrate,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        fetch_remote: bool = ...,
        validate_url: bool = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...
