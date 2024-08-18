"""
Runtime-protocols for the `copy` standard library.
https://docs.python.org/3/library/copy.html
"""
from __future__ import annotations

import sys


if sys.version_info >= (3, 13):
    from typing import Protocol, Self, TypeVar, override, runtime_checkable
else:
    from typing_extensions import Protocol, Self, TypeVar, override, runtime_checkable


__all__ = (
    'CanCopy', 'CanCopySelf',
    'CanDeepcopy', 'CanDeepcopySelf',
    'CanReplace', 'CanReplaceSelf',
)  # fmt: skip

_T_co = TypeVar('_T_co', covariant=True)
_V_contra = TypeVar('_V_contra', contravariant=True)
_AnyV_contra = TypeVar('_AnyV_contra', contravariant=True, default=object)


@runtime_checkable
class CanCopy(Protocol[_T_co]):
    """Anything that can be used as `copy.copy(_: CanCopy[T]) -> T`."""
    def __copy__(self, /) -> _T_co: ...


@runtime_checkable
class CanCopySelf(CanCopy['CanCopySelf'], Protocol):
    """Runtime-checkable alias `CanCopySelf = CanCopy[Self]`."""
    @override
    def __copy__(self, /) -> Self: ...


@runtime_checkable
class CanDeepcopy(Protocol[_T_co]):
    """Anything that can be used as `copy.deepcopy(_: CanDeepcopy[T]) -> T`."""
    def __deepcopy__(self, memo: dict[int, object], /) -> _T_co: ...


@runtime_checkable
class CanDeepcopySelf(CanDeepcopy['CanDeepcopySelf'], Protocol):
    """Runtime-checkable alias `CanDeepcopySelf = CanDeepcopy[Self]`."""
    @override
    def __deepcopy__(self, memo: dict[int, object], /) -> Self: ...


@runtime_checkable
class CanReplace(Protocol[_V_contra, _T_co]):
    """
    Anything that can be used as `copy.replace(_: CanReplace[-V, +T]) -> T` (since
    Python 3.13+).
    """
    def __replace__(self, /, **changes: _V_contra) -> _T_co: ...


@runtime_checkable
class CanReplaceSelf(
    CanReplace[_AnyV_contra, 'CanReplaceSelf[_AnyV_contra]'],
    Protocol[_AnyV_contra],
):
    """Runtime-checkable alias `CanReplaceSelf[-V = object] = CanReplace[V, Self]`."""
    @override
    def __replace__(self, /, **changes: _AnyV_contra) -> Self: ...
