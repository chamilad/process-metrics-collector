from pathlib import Path
from typing import (
    Any,
    Mapping,
    Optional,
)
from .file import File as File
from ..rocrate import ROCrate

class Preview(File):
    BASENAME: str
    def __init__(
        self,
        crate: ROCrate,
        source: Optional[str | Path] = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...
    def generate_html(self) -> str: ...
    def write(self, dest_base: str) -> None: ...
