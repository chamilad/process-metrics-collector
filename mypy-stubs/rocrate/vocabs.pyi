from typing import (
    Any,
    Mapping,
    Optional,
)

from .model.metadata import JSONLD

RO_CRATE: JSONLD
SCHEMA: JSONLD
SCHEMA_MAP: Mapping[str, Mapping[str, Any]]

def term_to_uri(name: str) -> str | Mapping[str, str]: ...
def schema_doc(uri: str) -> Optional[Mapping[str, Any]]: ...
