from pathlib import Path
from typing import (
    Any,
    Optional,
    Mapping,
    MutableSequence,
    MutableMapping,
    Sequence,
)
from typing_extensions import (
    Required,
    TypedDict,
    TypeAlias,
)

from .dataset import Dataset as Dataset
from .file import File as File
from ..rocrate import ROCrate

JSONLD_CONTEXT: TypeAlias = Mapping[str, str | Mapping[str, str]]
JSONLD_GRAPH_ITEM: TypeAlias = Mapping[str, Any]

JSONLD = TypedDict(
    "JSONLD",
    {
        "@context": Required[JSONLD_CONTEXT],
        "@graph": Required[Sequence[JSONLD_GRAPH_ITEM]],
    },
)

WORKFLOW_PROFILE: str

class Metadata(File):
    BASENAME: str
    PROFILE: str
    extra_terms: MutableMapping[str, str]
    extra_contexts: MutableSequence[str]
    def __init__(
        self,
        crate: ROCrate,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> None: ...
    def generate(self) -> JSONLD: ...
    def write(self, base_path: str) -> None: ...
    @property
    def root(self) -> Dataset: ...

class LegacyMetadata(Metadata):
    BASENAME: str
    PROFILE: str

TESTING_EXTRA_TERMS: Mapping[str, str]

def metadata_class(descriptor_id: str) -> Metadata: ...
