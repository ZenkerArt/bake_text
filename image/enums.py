from enum import Enum, auto


class IMAGE_ACTION(Enum):
    REMOVE_ALL = 'REMOVE_ALL'
    REMOVE = 'REMOVE'
    ADD = 'ADD'

    @classmethod
    def enum(cls):
        arr = []
        for i in cls:
            arr.append((i.value, i.value, ''))

        return arr
