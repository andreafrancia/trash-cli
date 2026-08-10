# AGENTS.md

## Python compatibility

The code is supposed to support Python 2.7 through 3.14 simultaneously. Avoid
syntax or stdlib features that don't exist across that whole range (e.g. no
f-strings, no `pathlib` as a hard dependency, no `match` statements).

## Development environment

Development uses a virtualenv at `.venv`. Activate it (`source .venv/bin/activate`)
or invoke its `python`/`pip` directly (e.g. `.venv/bin/python`) when running
commands, rather than relying on the system Python.

## Versioning

The version number is derived from the release date, not semantic versioning:
`0.YY.M.D` (e.g. `0.24.5.26` = released 2024-05-26). No leading zeros on
month/day. It lives in a single place, `trashcli/trash.py` (`version = '...'`),
and `setup.cfg` reads it from there via `version = attr: trashcli.trash.version`.
Git tags use the bare version string with no `v` prefix (e.g. `0.24.5.26`).

`scripts/bump` computes today's date version, refuses to run on a dirty
working tree, writes it into `trashcli/trash.py`, and commits it
(`Bump version to 'X'`). The logic lives in
`tests/support/tools/{bump_cmd,version_from_date,version_saver}.py` (yes, under
`tests/` — that's a pre-existing quirk, not a new decision).

`scripts/set-dev-version <ref> <sha>` writes a PEP 440 dev version
(`0.YY.M.D.dev0+git.<ref>.<sha>`) instead, used for CI build checks so those
runs never collide with a real release version.

## Release process

This section describes the process as it exists today. Release automation is
in progress — see `RELEASE-AUTOMATION.md` at the repo root for the target
process and current status; treat that file as more current than this one
until it says the migration is done.

Current (manual) steps:

1. `scripts/bump` locally to bump the version and commit it.
2. `git push origin master`.
3. Build the sdist locally (`python -m build --sdist`), `twine check` it,
   upload to TestPyPI, test-install from there.
4. `twine upload` the sdist to real PyPI.
5. `git tag <version>` and push the tag — this happens *after* the PyPI
   upload, and no GitHub Release object is ever created.

Full manual walkthrough: `docs/how-to-build-and-upload-a-new-release.rst`.

Two GitHub Actions workflows exist:

- `.github/workflows/run-tests.yml` — runs on every push and PR: the test
  matrix (Python 2.7-3.14, Linux/macOS), type checks, and an `sdist` job that
  builds the sdist and pip-installs it to confirm packaging works.
- `.github/workflows/make-release.yml` — runs on *every push to any branch*
  (not just tags/master). It sets a dev version and builds an sdist, then
  uploads it as a plain CI artifact via `actions/upload-artifact`. Despite the
  name, this does not create a GitHub Release and does not touch PyPI — it's
  effectively a duplicate of the `sdist` job above with a different version
  string.
