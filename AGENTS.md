# AGENTS.md

## Python compatibility

The code is supposed to support Python 2.7 through 3.14 simultaneously. Avoid
syntax or stdlib features that don't exist across that whole range (e.g. no
f-strings, no `pathlib` as a hard dependency, no `match` statements).

## Development environment

Development uses a virtualenv at `.venv`. Activate it (`source .venv/bin/activate`)
or invoke its `python`/`pip` directly (e.g. `.venv/bin/python`) when running
commands, rather than relying on the system Python.

## Git workflow

Do every new task in its own worktree, on its own branch, and integrate it
into `master` keeping the history linear (no merge commits).

1. Create the worktree and the branch from `master`, in a sibling directory,
   and work only there:

       git worktree add -b <task-branch> ../trash-cli-<task-branch> master

   Untracked directories such as `.venv` are not shared between worktrees:
   either create one in the new worktree or run the main checkout's
   `.venv/bin/python` from inside it.
2. Before committing the work of the task, always run `scripts/pre-push` from
   the task worktree and fix what it reports. It runs the tests (tox), the sdist
   smoke test, and the type checks for Python 3 and Python 2.7. The sdist smoke
   test uses a temporary trash and working directory, so the user's real trash
   is left alone.

   Then commit on the task branch.

   Every commit must pass `scripts/pre-push`, not only the last one of the
   task: run it before each commit, one commit at a time, and never batch
   several changes to test them together at the end.

   Rewriting the history (rebase, reorder, split, squash, reword) is the
   exception: you don't need to run `scripts/pre-push` on every rewritten
   commit. While rewriting, run only the check or the tests involved in what
   you are changing (for example `scripts/check-types`, or
   `.venv/bin/python -m pytest tests/path/test_x.py`). When the rewrite is
   finished, run `scripts/pre-push` once, on the tip. If it fails:

   1. find the commit that introduced the failure with `git bisect`, between
      the base of the rewrite (good) and the tip (bad). Bisect with the
      failing check or test, not the whole `scripts/pre-push`, for example
      `git bisect run .venv/bin/python -m pytest tests/path/test_x.py`;
   2. fix that commit with an interactive rebase (`edit` it), not with a
      fixup at the tip;
   3. run `scripts/pre-push` on the tip again.
3. Integrate into `master`:

       git rebase master                # in the task worktree
       git merge --ff-only <task-branch> # in the main checkout, on master

   If a merge commit ends up on `master` anyway, run `git rebase` with no
   arguments there: it replays the local commits on top of `origin/master`
   (the upstream of `master`) and drops the merge commit.
4. Remove the worktree and the branch once integrated:

       git worktree remove ../trash-cli-<task-branch>
       git branch -d <task-branch>

Never rewrite published history. Published commits are the ones reachable from
`origin/master`: run `git fetch`, and only rebase, amend or reset commits listed
by `git log origin/master..HEAD`. Never force-push.
