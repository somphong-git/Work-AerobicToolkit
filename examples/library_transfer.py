"""Export portable metadata and create a complete catalog backup."""

from aerobictoolkit.library import backup_library, export_library

export_library("data/reports/library.json")
export_library("data/reports/library.csv")
backup_library("data/output/catalog-backup.sqlite3")
