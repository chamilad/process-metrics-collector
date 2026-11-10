from typing import (
    Any,
    Mapping,
    Optional,
)

from .contextentity import ContextEntity as ContextEntity
from ..rocrate import ROCrate

class Person(ContextEntity):
    def __init__(
        self,
        crate: ROCrate,
        identifier: Optional[Any] = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...
