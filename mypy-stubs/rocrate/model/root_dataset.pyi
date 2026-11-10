from pathlib import Path
from typing import (
    Any,
    Mapping,
    Optional,
)

from ..utils import iso_now as iso_now
from .dataset import Dataset as Dataset
from ..rocrate import ROCrate

class RootDataset(Dataset):
    def __init__(
        self,
        crate: ROCrate,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...
