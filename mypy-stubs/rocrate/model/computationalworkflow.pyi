from pathlib import Path
from typing import (
    Optional,
    Sequence,
)

from .entity import (
    Entity,
    EntityRef,
)
from .file import File as File

class ComputationalWorkflow(File):
    TYPES: Sequence[str]

    @property
    def programmingLanguage(self) -> Optional[str | Entity | EntityRef]: ...
    @programmingLanguage.setter
    def programmingLanguage(
        self, programmingLanguage: str | Entity | EntityRef
    ) -> None: ...
    @property
    def lang(self) -> Optional[str | Entity | EntityRef]: ...
    @lang.setter
    def lang(self, programmingLanguage: str | Entity | EntityRef) -> None: ...
    @property
    def language(self) -> Optional[str | Entity | EntityRef]: ...
    @language.setter
    def language(self, programmingLanguage: str | Entity | EntityRef) -> None: ...
    @property
    def subjectOf(self) -> Optional[str | Entity | EntityRef]: ...
    @subjectOf.setter
    def subjectOf(self, subjectOf: str | Entity | EntityRef) -> None: ...

class WorkflowDescription(ComputationalWorkflow):
    TYPES: Sequence[str]

class Workflow(ComputationalWorkflow):
    TYPES: Sequence[str]

def galaxy_to_abstract_cwl(workflow_path: str | Path, delete: bool = ...) -> str: ...
