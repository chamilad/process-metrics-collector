from typing import (
    Optional,
)

from .entity import EntityRef
from .file import File as File

class TestDefinition(File):
    @property
    def engineVersion(self) -> Optional[str]: ...
    @engineVersion.setter
    def engineVersion(self, version: str) -> None: ...
    @property
    def conformsTo(self) -> Optional[str | EntityRef]: ...
    @conformsTo.setter
    def conformsTo(self, url: str | EntityRef) -> None: ...

    engine = conformsTo
