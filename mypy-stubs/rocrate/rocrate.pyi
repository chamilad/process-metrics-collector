import datetime
from pathlib import Path
from typing import (
    Any,
    Iterable,
    Mapping,
    MutableSequence,
    Optional,
    overload,
    Sequence,
    Set,
    TypeVar,
)
from uuid import UUID

from .metadata import (
    find_root_entity_id as find_root_entity_id,
    read_metadata as read_metadata,
)
from .model.computationalworkflow import (
    ComputationalWorkflow as ComputationalWorkflow,
    WorkflowDescription as WorkflowDescription,
    galaxy_to_abstract_cwl as galaxy_to_abstract_cwl,
)
from .model.computerlanguage import (
    ComputerLanguage as ComputerLanguage,
    get_lang as get_lang,
)
from .model.contextentity import ContextEntity as ContextEntity
from .model.data_entity import DataEntity as DataEntity
from .model.dataset import Dataset as Dataset
from .model.entity import (
    Entity as Entity,
    EntityRef,
)
from .model.file import File as File
from .model.file_or_dir import FileOrDir as FileOrDir
from .model.metadata import (
    JSONLD,
    LegacyMetadata as LegacyMetadata,
    Metadata as Metadata,
    TESTING_EXTRA_TERMS as TESTING_EXTRA_TERMS,
    WORKFLOW_PROFILE as WORKFLOW_PROFILE,
    metadata_class as metadata_class,
)
from .model.preview import Preview as Preview
from .model.root_dataset import RootDataset as RootDataset
from .model.softwareapplication import (
    SoftwareApplication as SoftwareApplication,
    get_app as get_app,
)
from .model.testdefinition import TestDefinition as TestDefinition
from .model.testinstance import TestInstance as TestInstance
from .model.testservice import TestService as TestService, get_service as get_service
from .model.testsuite import TestSuite as TestSuite
from .utils import (
    get_norm_value as get_norm_value,
    is_url as is_url,
    subclasses as subclasses,
    walk as walk,
)

_ETYPE = TypeVar("_ETYPE", bound=Entity)

def pick_type(
    json_entity: Mapping[str, Any],
    type_map: Mapping[str, type[Entity]],
    fallback: Optional[type[Entity]] = ...,
) -> type[Entity]: ...

class ROCrate:
    exclude: Optional[Sequence[str] | Set[str]]
    default_entities: MutableSequence[RootDataset | Metadata | Preview]
    data_entities: MutableSequence[File | Dataset | DataEntity | Metadata]
    contextual_entities: MutableSequence[Entity]
    uuid: UUID
    arcp_base_uri: str
    preview: Optional[Preview]
    source: Optional[str | Path]
    def __init__(
        self,
        source: Optional[str | Path] = ...,
        gen_preview: bool = ...,
        init: bool = ...,
        version: str = ...,
        exclude: Optional[Sequence[str] | Set[str]] = ...,
    ) -> None: ...
    @property
    def name(self) -> Optional[str]: ...
    @name.setter
    def name(self, name: str) -> None: ...
    @property
    def datePublished(self) -> Optional[datetime.datetime]: ...
    @datePublished.setter
    def datePublished(self, value: str | datetime.datetime) -> None: ...
    @property
    def creator(self) -> Optional[str | Entity]: ...
    @creator.setter
    def creator(self, creator: str | Entity) -> None: ...
    @property
    def license(self) -> Optional[str | Entity | Sequence[str | Entity]]: ...
    @license.setter
    def license(self, license: str | Entity | Sequence[str | Entity]) -> None: ...
    @property
    def description(self) -> Optional[str]: ...
    @description.setter
    def description(self, description: str) -> None: ...
    @property
    def keywords(self) -> Optional[Any]: ...
    @property
    def publisher(self) -> Optional[Any]: ...
    @property
    def isBasedOn(self) -> Optional[str | EntityRef]: ...
    @isBasedOn.setter
    def isBasedOn(self, isBasedOn: str | EntityRef) -> None: ...
    @property
    def image(self) -> Optional[Any]: ...
    @property
    def CreativeWorkStatus(self) -> Optional[Any]: ...
    @property
    def mainEntity(self) -> Optional[Entity]: ...
    @mainEntity.setter
    def mainEntity(self, mainEntity: Entity) -> None: ...
    @property
    def test_dir(self) -> Optional[Dataset]: ...
    @property
    def examples_dir(self) -> Optional[Dataset]: ...
    @property
    def test_suites(self) -> Sequence[TestSuite]: ...
    def resolve_id(self, id_: str) -> str: ...
    def get_entities(self) -> Iterable[Entity]: ...
    def dereference(
        self, entity_id: str, default: Optional[Entity] = ...
    ) -> Optional[Entity]: ...
    get = dereference
    def add_file(
        self,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        fetch_remote: bool = ...,
        validate_url: bool = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> File: ...
    def add_dataset(
        self,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        fetch_remote: bool = ...,
        validate_url: bool = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> Dataset: ...
    add_directory = add_dataset
    def add_tree(
        self,
        source: str | Path,
        dest_path: Optional[str] = ...,
        properties: Optional[Mapping[str, Any]] = ...,
    ) -> Dataset: ...
    root_dataset: RootDataset
    metadata: Metadata
    @overload
    def add(self, entity: _ETYPE) -> _ETYPE: ...  # type: ignore[misc]
    @overload
    def add(self, *entities: _ETYPE) -> Sequence[_ETYPE]: ...
    def delete(self, *entities: Entity) -> None: ...
    def write(self, base_path: str | Path) -> None: ...
    write_crate = write
    def write_zip(self, out_path: str | Path) -> str: ...
    def add_workflow(
        self,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        fetch_remote: bool = ...,
        validate_url: bool = ...,
        properties: Optional[Mapping[str, Any]] = ...,
        main: bool = ...,
        lang: str | ComputerLanguage = ...,
        lang_version: Optional[str] = ...,
        gen_cwl: bool = ...,
        cls: type[ComputationalWorkflow] = ...,
    ) -> ComputationalWorkflow: ...
    def add_test_suite(
        self,
        identifier: Optional[Any] = ...,
        name: Optional[str] = ...,
        main_entity: Optional[Entity] = ...,
    ) -> TestSuite: ...
    def add_test_instance(
        self,
        suite: str | TestSuite,
        url: str,
        resource: str = ...,
        service: str = ...,
        identifier: Optional[Any] = ...,
        name: Optional[str] = ...,
    ) -> TestInstance: ...
    def add_test_definition(
        self,
        suite: str | TestSuite,
        source: Optional[str | Path] = ...,
        dest_path: Optional[str] = ...,
        fetch_remote: bool = ...,
        validate_url: bool = ...,
        properties: Optional[Mapping[str, Any]] = ...,
        engine: str = ...,
        engine_version: Optional[str] = ...,
    ) -> TestDefinition: ...
    def add_jsonld(self, jsonld: JSONLD) -> ContextEntity: ...
    def update_jsonld(self, jsonld: JSONLD) -> Entity: ...
    def add_or_update_jsonld(self, jsonld: JSONLD) -> Entity: ...

def make_workflow_rocrate(
    workflow_path: str,
    wf_type: str,
    include_files: Sequence[str | Path] = ...,
    fetch_remote: bool = ...,
    cwl: Optional[Any] = ...,
    diagram: Optional[Any] = ...,
) -> ROCrate: ...
