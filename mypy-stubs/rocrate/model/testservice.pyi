from typing import (
    Callable,
    Mapping,
    Optional,
)

from .entity import EntityRef
from .contextentity import ContextEntity as ContextEntity
from ..rocrate import ROCrate

class TestService(ContextEntity):
    @property
    def name(self) -> Optional[str]: ...
    @name.setter
    def name(self, name: str) -> None: ...
    @property
    def url(self) -> Optional[str | EntityRef]: ...
    @url.setter
    def url(self, url: str | EntityRef) -> None: ...

JENKINS_ID: str
TRAVIS_ID: str
GITHUB_ID: str

def jenkins(crate: ROCrate) -> TestService: ...
def travis(crate: ROCrate) -> TestService: ...
def github(crate: ROCrate) -> TestService: ...

SERVICE_MAP: Mapping[str, Callable[[ROCrate], TestService]]

def get_service(crate: ROCrate, name: str) -> TestService: ...
