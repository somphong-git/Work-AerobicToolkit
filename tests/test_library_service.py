from pathlib import Path

from aerobictoolkit.analysis import BatchAnalysisResult, BatchTrackAnalysis
from aerobictoolkit.library import LibraryCatalog
from aerobictoolkit.library.service import index_directory

from .test_library import make_analysis


def test_index_directory_persists_all_successful_tracks(
    tmp_path: Path, monkeypatch
) -> None:
    batch = BatchAnalysisResult(
        directory=tmp_path,
        tracks=(
            BatchTrackAnalysis(make_analysis(tmp_path / "one.wav"), False),
            BatchTrackAnalysis(make_analysis(tmp_path / "two.wav"), True),
        ),
        errors=(),
    )
    monkeypatch.setattr(
        "aerobictoolkit.library.service.analyze_directory",
        lambda *args, **kwargs: batch,
    )
    database = tmp_path / "catalog.db"

    result = index_directory(tmp_path, database_path=database)

    assert result.indexed == 2
    assert result.cache_hits == 1
    with LibraryCatalog(database) as catalog:
        assert len(catalog.search()) == 2
