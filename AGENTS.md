# AGENTS.md

## Development Process

- **TDD**: for any new behavior, write a failing test first, then the minimal code to
  make it pass.
- **Incrementalism**: implement one scenario/test at a time, never batch multiple
  scenarios into a single change.
- **Happy path first**: when a feature has several scenarios, implement the core/happy
  path completely before edge cases, error paths, and flag-interaction cases.
- **Commit-on-green only**: run the full test suite (`pytest`) before every commit.
  Only commit when it is fully green. Never commit with a failing or erroring test.
- **One commit per newly-green test** (during feature work driven by a todo list): after
  a test goes from red to green, run the full suite, then commit immediately, then check
  off that item in the feature's todo list as part of the same commit.
