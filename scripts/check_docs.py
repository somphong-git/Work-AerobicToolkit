"""Verify that the repository's required documentation entry points exist."""

from __future__ import annotations

from pathlib import Path

REQUIRED_DOCUMENTS = (
    Path("README.md"),
    Path("docs/architecture.md"),
    Path("docs/roadmap.md"),
    Path("docs/installation.md"),
    Path("docs/developer-guide.md"),
    Path("docs/user-guide.md"),
    Path("docs/faq.md"),
    Path("docs/decisions/ADR-0001-project-layout.md"),
    Path("docs/decisions/ADR-0002-audio-engine.md"),
    Path("docs/decisions/ADR-0003-plugin-system.md"),
)


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for relative_path in REQUIRED_DOCUMENTS:
        path = repository_root / relative_path
        if not path.is_file():
            errors.append(f"Missing documentation file: {relative_path}")
            continue

        if not path.read_text(encoding="utf-8").lstrip().startswith("# "):
            errors.append(f"Documentation file needs an H1 heading: {relative_path}")

    if errors:
        print("\n".join(errors))
        return 1

    print(f"Validated {len(REQUIRED_DOCUMENTS)} documentation entry points.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
