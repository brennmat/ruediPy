from importlib.metadata import PackageNotFoundError, version

from .misc import get_logger, set_have_external_gui

__all__ = ["get_logger", "set_have_external_gui"]

try:
	__version__ = version("ruediPy")
except PackageNotFoundError:
	__version__ = "0+unknown"

