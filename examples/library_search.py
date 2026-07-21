"""Build and query a metadata-only local music catalog."""

from aerobictoolkit.library import LibraryCatalog, LibraryQuery, index_directory

index_directory("data/input", include_bpm=False)

with LibraryCatalog() as catalog:
    tracks = catalog.search(LibraryQuery(tags=("warmup",), limit=20))
    for track in tracks:
        print(track.title, track.bpm, track.tags)
