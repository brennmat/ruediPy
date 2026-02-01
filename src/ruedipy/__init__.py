from importlib.metadata import PackageNotFoundError, version

__all__ = []

try:
	__version__ = version("ruediPy")
except PackageNotFoundError:
	__version__ = "0+unknown"

