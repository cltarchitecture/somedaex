import random
import string
from typing import Generic, TypeVar
from .proxy import ObservableProxy

T = TypeVar("T")


class ObservableProperty(Generic[T]):
    """A property descriptor that defines an attribute backed by an ObservableProxy.

    This descriptor enables assignment to the attribute without overwriting the
    ObservableProxy instance."""

    def __init__(self, doc: str = None, proxy=ObservableProxy):
        self.name = ""
        self.internal_name = ""
        self.proxy_class = proxy
        if doc is not None:
            self.__doc__ = doc

    def __set_name__(self, owner, name):
        self.name = name
        unique = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        self.internal_name = "_" + name + "_" + unique

    def __get__(self, obj, objtype=None) -> T:
        return getattr(obj, self.internal_name)

    def __set__(self, obj, value: T):
        if hasattr(obj, self.internal_name):
            proxied_value = getattr(obj, self.internal_name)
            proxied_value.__wrapped__ = value
            proxied_value.__observable__.on_next(value)
        else:
            proxied_value = self.proxy_class(value)
            setattr(obj, self.internal_name, proxied_value)
