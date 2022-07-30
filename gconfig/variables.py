from abc import ABC, abstractmethod
from typing import Generic, Iterable, Any, TypeVar

from numpy import ndarray

_T = TypeVar('_T')


def arr_to_text(arr: Iterable[Any]):
    return ','.join(str(i) for i in arr)


class GVar(ABC, Generic[_T]):
    @abstractmethod
    def value(self) -> _T:
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass


class GVarWithID(GVar, ABC):
    @abstractmethod
    def id(self) -> str:
        pass


class GVector(GVarWithID):
    _vector: ndarray
    _id: str

    def __init__(self, obj_id: str, vector: ndarray = None):
        self._id = obj_id
        self._vector = vector

    def id(self):
        return self._id

    def value(self) -> ndarray:
        return self._vector

    def to_string(self) -> str:
        return f'{self._id},{arr_to_text((self._vector[0], self._vector[2], self._vector[1]))}'
