from .contextentity import ContextEntity as ContextEntity

from typing import (
    Optional,
)

class TestSuite(ContextEntity):
    @property
    def name(self) -> Optional[str]: ...
    @name.setter
    def name(self, name: str) -> None: ...
    @property
    def instance(self) -> str: ...
    @property
    def definition(self) -> str: ...
