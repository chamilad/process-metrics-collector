from collections.abc import Generator

from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
)

def is_url(string: str) -> bool: ...
def iso_now() -> str: ...
def subclasses(cls: type[object]) -> Generator[type[object], None, None]: ...
def get_norm_value(json_entity: Mapping[str, Any], prop: str) -> Sequence[str]: ...
def walk(
    top: str,
    topdown: bool = ...,
    onerror: Optional[Callable[[OSError], None]] = ...,
    followlinks: bool = ...,
    exclude: Optional[Sequence[str] | Set[str]] = ...,
) -> Generator[Tuple[str, Sequence[str], Sequence[str]], None, None]: ...
