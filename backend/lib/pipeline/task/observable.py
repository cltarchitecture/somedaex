from copy import copy
from typing import Any, Callable, Type, TypeVar, Union

from rx.core.typing import Observable
from rx.operators import first
from rx.subject import BehaviorSubject, Subject


T = TypeVar("T")


class ObservableValue(Observable[T]):

    __slots__ = "observable"

    def __init__(self, value: T):
        self.observable = BehaviorSubject(value)

    @property
    def value(self) -> T:
        return self.observable.value

    @value.setter
    def value(self, value: T):
        self.observable.on_next(value)

    def subscribe(self, *args, **kwargs):
        return self.observable.subscribe(*args, **kwargs)

    def pipe(self, *args, **kwargs):
        return self.observable.pipe(*args, **kwargs)

    def __eq__(self, other: Union[T, "ObservableValue[T]"]) -> bool:
        if isinstance(other, ObservableValue):
            other = other.value
        return self.value == other

    def __str__(self):
        return str(self.observable.value)

    def satisfies(self, predicate: Callable[[T], bool]) -> Observable[T]:
        return self.pipe(first(predicate))

    def equals(self, value: T) -> Observable[T]:
        return self.pipe(first(lambda x: x == value))

    def update(self, updater: Callable[[T], T], inplace=False):
        copied = copy(self.observable.value)
        modified = updater(copied)
        self.observable.on_next(copied if inplace else modified)

    def __getitem__(self, key: Any) -> T:
        return self.observable.value[key]


# class ObservableDict(ObservableValue[T]):
#     def __getitem__(self, key) -> T:
#         return self.observable.value[key]

#     def _modify(self, fn):
#         new_dict = self.observable.value.copy()
#         retval = fn(new_dict)
#         self.observable.on_next(new_dict)
#         return retval

#     def __setitem__(self, key, value: T):
#         return self._modify(lambda d: d.__setitem__(key, value))

#     def __delitem__(self, key):
#         return self._modify(lambda d: d.__delitem__(key))

#     def update(self, other):
#         return self._modify(lambda d: d.update(other))

#     def pop(self, key) -> T:
#         return self._modify(lambda d: d.pop(key))


class ObservableEvent(Subject):
    def emit(self, reason=None):
        self.on_next(reason)
