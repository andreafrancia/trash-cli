# AGENTS.md

## Python compatibility

The code is supposed to support Python 2.7 through 3.14 simultaneously. Avoid
syntax or stdlib features that don't exist across that whole range (e.g. no
f-strings, no `pathlib` as a hard dependency, no `match` statements).

## Development environment

Development uses a virtualenv at `.venv`. Activate it (`source .venv/bin/activate`)
or invoke its `python`/`pip` directly (e.g. `.venv/bin/python`) when running
commands, rather than relying on the system Python.
