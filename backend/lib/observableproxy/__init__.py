"""The observableproxy package provides a way to monitor changes to the value of
an otherwise ordinary-looking variable."""

from .proxy import observe, ObservableProxy
from .property import ObservableProperty
