"""Public API for the persistent local music library."""

from .catalog import DEFAULT_LIBRARY_PATH, LibraryCatalog
from .models import LibraryIndexResult, LibraryQuery, LibraryTrack
from .service import index_directory

__all__ = [
    "DEFAULT_LIBRARY_PATH",
    "LibraryCatalog",
    "LibraryIndexResult",
    "LibraryQuery",
    "LibraryTrack",
    "index_directory",
]
