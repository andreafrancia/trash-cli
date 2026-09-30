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
2. Commit on the task branch, then run the checks (see the development
   environment above).
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
