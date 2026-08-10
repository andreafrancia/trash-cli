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

Cutting a release takes three actions, none of them local commands, in this
order:

1. **Bump the version.** On GitHub: Actions -> "Bump version" ->
   Run workflow (on `master`). This runs `scripts/bump` in CI, commits
   `Bump version to 'X'`, tags it `X` (bare version string, no `v` prefix,
   e.g. `0.24.8.10`), and pushes both. Workflow:
   `.github/workflows/bump-version.yml`.
2. **Draft and publish a GitHub Release** on that new tag, via the normal
   GitHub web UI ("Draft a new release" -> choose the tag just pushed).
   Publishing the release (the `release: published` event) triggers
   `.github/workflows/publish-release.yml`, which builds the sdist,
   `twine check`s it, and attaches it to the Release as a downloadable asset.
   That workflow also uploads the sdist as a build artifact for the next
   step.
3. **Approve the PyPI publish.** The same workflow has a second job,
   `publish-pypi`, gated behind the `pypi` GitHub Environment (required
   reviewer + a tag-name policy limited to `0.[0-9]*.[0-9]*.[0-9]*`). The
   workflow run pauses at "Review deployments"; approving it publishes the
   already-built sdist to PyPI via `pypa/gh-action-pypi-publish`, using PyPI
   Trusted Publishing (OIDC) — there is no PyPI API token stored anywhere in
   this repo, and this job is never reachable from a `pull_request`-triggered
   run, so approving a fork PR's workflow run can never trigger a PyPI
   publish.

No TestPyPI step: `run-tests.yml`'s `sdist` job already builds, installs, and
exercises every CLI command on every push, which was TestPyPI's only real
value here.

One-time setup required before this works (not part of the workflows
themselves): a PyPI Trusted Publisher entry for this repo/workflow/
environment, and the `pypi` GitHub Environment's protection rules. See
`docs/release-setup-manual.md` for the exact steps, and `RELEASE-AUTOMATION.md`
for how each piece was built and verified.

Workflows involved:

- `.github/workflows/run-tests.yml` — runs on every push and PR: the test
  matrix (Python 2.7-3.14, Linux/macOS), type checks, and an `sdist` job that
  builds the sdist and pip-installs it to confirm packaging works.
- `.github/workflows/bump-version.yml` — manual (`workflow_dispatch` only):
  bump, commit, tag, push.
- `.github/workflows/publish-release.yml` — triggered by `release: published`:
  build sdist + attach to Release, then (gated) publish to PyPI.
