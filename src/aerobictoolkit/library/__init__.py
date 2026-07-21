"""Public API for the persistent local music library."""

from .catalog import DEFAULT_LIBRARY_PATH, LibraryCatalog
from .models import LibraryImportResult, LibraryIndexResult, LibraryQuery, LibraryTrack
from .service import index_directory
from .transfer import backup_library, export_library, import_library

__all__ = [
    "DEFAULT_LIBRARY_PATH",
    "LibraryCatalog",
    "LibraryImportResult",
    "LibraryIndexResult",
    "LibraryQuery",
    "LibraryTrack",
    "backup_library",
    "export_library",
    "import_library",
    "index_directory",
]
