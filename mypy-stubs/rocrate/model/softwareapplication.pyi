from typing import (
    Callable,
    Mapping,
    Optional,
)

from .contextentity import ContextEntity as ContextEntity
from .creativework import CreativeWork as CreativeWork
from .entity import EntityRef
from ..rocrate import ROCrate

class SoftwareApplication(ContextEntity, CreativeWork):
    @property
    def name(self) -> Optional[str]: ...
    @name.setter
    def name(self, name: str) -> None: ...
    @property
    def url(self) -> Optional[str | EntityRef]: ...
    @url.setter
    def url(self, url: str | EntityRef) -> None: ...
    @property
    def version(self) -> Optional[str | EntityRef]: ...
    @version.setter
    def version(self, url: str | EntityRef) -> None: ...

PLANEMO_ID: str

def planemo(crate: ROCrate) -> SoftwareApplication: ...

APP_MAP: Mapping[str, Callable[[ROCrate], SoftwareApplication]]

def get_app(crate: ROCrate, name: str) -> SoftwareApplication: ...
