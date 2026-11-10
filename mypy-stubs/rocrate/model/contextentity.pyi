from typing import (
    Any,
    Mapping,
    Optional,
)

from ..utils import is_url as is_url
from .entity import Entity as Entity

from ..rocrate import ROCrate

def add_hash(id_: Optional[str]) -> str: ...

class ContextEntity(Entity):
    def __init__(
        self,
        crate: ROCrate,
        identifier: Optional[Any] = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...
    def format_id(self, identifier: str) -> str: ...
