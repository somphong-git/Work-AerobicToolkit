# Frequently Asked Questions

## Is this ready to create a DJ mix?

No. Version 0.2.0 establishes the development foundation. Audio analysis and
mix generation will be introduced through future issue-driven sprints.

## Why use a `src/` layout?

It keeps importable product code separate from repository files and makes tests
exercise the installed package boundary rather than accidentally importing from
the working directory.

## Where should audio files be stored?

Use `data/input/` for local source files. Do not commit copyrighted music,
generated audio, reports, or cache data.

## Why are there placeholder examples and test modules?

They establish discoverable extension points without presenting unfinished
product behavior as complete. Each will gain real examples and assertions when
its corresponding feature issue is approved.

## How do I propose a feature?

Open an issue using the feature request form, describe the user problem and
acceptance criteria, then discuss scope before implementation starts.
