from pathlib import Path
from typing import (
    Mapping,
    Tuple,
)

from .model.metadata import (
    JSONLD_CONTEXT,
    JSONLD_GRAPH_ITEM,
    LegacyMetadata as LegacyMetadata,
    Metadata as Metadata,
)

def read_metadata(
    metadata_path: str | Path,
) -> Tuple[JSONLD_CONTEXT, Mapping[str, JSONLD_GRAPH_ITEM]]: ...
def find_root_entity_id(
    entities: Mapping[str, JSONLD_GRAPH_ITEM],
) -> Tuple[str, str]: ...
