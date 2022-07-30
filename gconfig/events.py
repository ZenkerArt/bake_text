from dataclasses import dataclass
from typing import Union, Iterable

from numpy import ndarray
import numpy

from .variables import GVar, GVector


@dataclass
class GEvent:
    time: float
    name: str
    data: GVar

    def to_dict(self):
        return {
            'time': self.time,
            'data': [
                self.name,
                self.data.to_string()
            ]
        }


class GEventPool:
    _events: list[GEvent]
    _sums: dict[str, float]

    def __init__(self):
        self._events = []
        self.set_position = self._set_vector('SetPosition')
        self.set_rotation = self._set_vector('SetRotation')
        self.set_scale = self._set_vector('SetScale')
        self._sums = {}

    def _set_vector(self, name: str):
        def func(time: float, obj_id: str, vector: ndarray):
            if isinstance(vector, Iterable):
                vector = numpy.array(vector)

            s = self._sums.get(name)
            self._sums[name] = sum(vector)

            if s != sum(vector):
                self._events.append(GEvent(
                    time=time,
                    name=name,
                    data=GVector(obj_id, vector)
                ))
                self._sums[name] = sum(vector)

        return func

    @property
    def events(self):
        return self._events

    def add(self, data: Union[list[GEvent], 'GEventPool']):
        if isinstance(data, GEventPool):
            self._events.extend(data._events)
            return

        self._events.extend(data)

    def to_list(self):
        return [i.to_dict() for i in self._events]
