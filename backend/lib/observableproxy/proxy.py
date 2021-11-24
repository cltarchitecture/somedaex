from copy import copy
import decimal
import fractions
from typing import Callable, TypeVar

from rx.core.typing import Observable
from rx.subject import BehaviorSubject
import rx.operators
import wrapt


def call_and_publish_changes(wrapped, proxy, args, kwargs):
    """Check for changes in a wrapped object that occur as a result of calling
    a method."""
    original = copy(proxy.__wrapped__)
    retval = wrapped(*args, **kwargs)

    if proxy.__wrapped__ != original:
        proxy.__observable__.on_next(proxy.__wrapped__)

    return retval


wrap_own_method = wrapt.decorator(call_and_publish_changes)


# pylint: disable=invalid-name, too-few-public-methods
class wrap_attr_method:
    """A decorator that reports changes in the value of the given object proxy."""

    __slots__ = ("proxy",)

    def __init__(self, proxy):
        self.proxy = proxy

    @wrapt.decorator
    def __call__(self, wrapped, _, args, kwargs):
        return call_and_publish_changes(wrapped, self.proxy, args, kwargs)


def is_immutable_builtin(obj):
    """Return true if the given object is of an immutable built-in type."""
    return isinstance(
        obj,
        (
            int,
            float,
            complex,
            bool,
            str,
            bytes,
            tuple,
            range,
            frozenset,
            fractions.Fraction,
            decimal.Decimal,
        ),
    )


class ObservableProxy(wrapt.ObjectProxy):
    """An ObservableProxy proxies another object while monitoring changes to
    that object and publishing those changes via an RxPy observable."""

    __slots__ = ("__observable__",)

    def __init__(self, value):
        super().__init__(value)
        self.__observable__ = BehaviorSubject(value)

    def __del__(self):
        self.__observable__.dispose()

    __iadd__ = wrap_own_method(wrapt.ObjectProxy.__iadd__)
    __isub__ = wrap_own_method(wrapt.ObjectProxy.__isub__)
    __imul__ = wrap_own_method(wrapt.ObjectProxy.__imul__)
    __itruediv__ = wrap_own_method(wrapt.ObjectProxy.__itruediv__)
    __ifloordiv__ = wrap_own_method(wrapt.ObjectProxy.__ifloordiv__)
    __imod__ = wrap_own_method(wrapt.ObjectProxy.__imod__)
    __ipow__ = wrap_own_method(wrapt.ObjectProxy.__ipow__)
    __ilshift__ = wrap_own_method(wrapt.ObjectProxy.__ilshift__)
    __irshift__ = wrap_own_method(wrapt.ObjectProxy.__irshift__)
    __iand__ = wrap_own_method(wrapt.ObjectProxy.__iand__)
    __ixor__ = wrap_own_method(wrapt.ObjectProxy.__ixor__)
    __ior__ = wrap_own_method(wrapt.ObjectProxy.__ior__)
    __setitem__ = wrap_own_method(wrapt.ObjectProxy.__setitem__)
    __delitem__ = wrap_own_method(wrapt.ObjectProxy.__delitem__)

    # AttributeError: type object 'ObjectProxy' has no attribute '__idiv__'
    # __idiv__ = wrap_own_method(wrapt.ObjectProxy.__idiv__)

    # AttributeError: type object 'ObjectProxy' has no attribute '__setslice__'
    # __setslice__ = wrap_own_method(wrapt.ObjectProxy.__setslice__)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if not is_immutable_builtin(value):
            proxy = ObservableProxy(value)
            proxy.__observable__.pipe(
                rx.operators.map(lambda _: self.__wrapped__)
            ).subscribe(self.__observable__)
            return proxy
        return value

    def __getattr__(self, name):
        attr = super().__getattr__(name)
        if callable(attr):
            return wrap_attr_method(self)(attr)
        if not is_immutable_builtin(attr):
            proxy = ObservableProxy(attr)
            proxy.__observable__.pipe(
                rx.operators.map(lambda _: self.__wrapped__)
            ).subscribe(self.__observable__)
            return proxy
        return attr

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ("__wrapped__", "__observable__"):
            self.__observable__.on_next(self)

    def __delattr__(self, name):
        if name == "__observable__":
            raise TypeError("__observable__ cannot be deleted")
        super().__delattr__(name)


T = TypeVar("T")

# pylint: disable=invalid-name
class observe(Observable[T]):
    """Expose an observable that broadcasts changes to the underlying value of
    an ObservableProxy."""

    def __init__(self, proxy: T):
        if not isinstance(proxy, ObservableProxy):
            raise TypeError("Argument to observe() must be an ObservableProxy")
        self.proxy = proxy

    def subscribe(self, *args, **kwargs) -> Observable[T]:
        """Subscribe to changes in the value of the observed object."""
        return self.proxy.__observable__.subscribe(*args, **kwargs)

    def pipe(self, *args, **kwargs):
        """Pipe the observed values through the given operators."""
        return self.proxy.__observable__.pipe(*args, **kwargs)

    def satisfies(self, predicate: Callable[[T], bool]) -> Observable[T]:
        """Return an observable sequence that terminates when the observed value
        satisfies the given predicate function.

        The returned observable can be awaited to delay script execution util a
        certain condition is met.
        """
        return self.pipe(rx.operators.first(predicate))

    def equals(self, value: T) -> Observable[T]:
        """Return an observable sequence that terminates when the observed value
        equals the given test value.

        The returned observable can be awaited to delay script execution util a
        certain condition is met.
        """
        return self.pipe(rx.operators.first(lambda x: x == value))
