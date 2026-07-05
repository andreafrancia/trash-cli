# `trash-list --show-non-trashinfo` — Acceptance Scenarios

This is a human-readable specification (Gherkin structure, shell transcripts as the
literal step content). It is documentation only, not machine-parsed — the executable
tests are plain pytest in `tests/test_list/cmd/test_show_non_trashinfo.py`.

## Locked-in behavior

- `--show-non-trashinfo` is **exclusive**: when passed, only orphan paths (files under a
  trash dir's `files/` with no matching `.trashinfo` in `info/`) are printed; normal
  trashinfo entries are suppressed entirely.
- Line format is just the raw path to the orphan file under `files/` — no date, no
  original location.
- Respects the same `--trash-dir` / `--all-users` selection as normal listing.
- `--size` and/or `--files` combined with `--show-non-trashinfo` are ignored (they have
  no meaningful data for an orphan), and a warning is printed to stderr — the orphan
  output still proceeds (exit code 0).
- Warning text lists ignored flags in alphabetical order, regardless of the order they
  were typed on the command line:
  - `trash-list: --files is ignored when --show-non-trashinfo is used`
  - `trash-list: --size is ignored when --show-non-trashinfo is used`
  - `trash-list: --files and --size are ignored when --show-non-trashinfo is used`

## Scenario 1: Orphan shown, normal entry suppressed (happy path)

Given:
    $ touch file1
    $ trash-put file1
    $ touch ~/.local/share/Trash/files/orphan1

When:
    $ trash-list --show-non-trashinfo

Then stdout is exactly:
    /home/user/.local/share/Trash/files/orphan1

(note: no line for `file1` — exclusive mode)

## Scenario 2: No orphans → empty output

Given:
    $ touch file1
    $ trash-put file1

When:
    $ trash-list --show-non-trashinfo

Then stdout is empty, and exit code is 0.

## Scenario 3: Multiple orphans

Given:
    $ touch ~/.local/share/Trash/files/orphan1
    $ touch ~/.local/share/Trash/files/orphan2

When:
    $ trash-list --show-non-trashinfo

Then stdout is exactly:
    /home/user/.local/share/Trash/files/orphan1
    /home/user/.local/share/Trash/files/orphan2

## Scenario 4: Flag absent → orphan invisible (regression guard)

Given:
    $ touch ~/.local/share/Trash/files/orphan1

When:
    $ trash-list

Then stdout does not contain `orphan1`.

## Scenario 5: Respects `--trash-dir` selection

Given:
    $ touch /disk1/.Trash-1000/files/orphan1
    $ touch /disk2/.Trash-1000/files/orphan2

When:
    $ trash-list --show-non-trashinfo --trash-dir /disk1/.Trash-1000

Then stdout is exactly:
    /disk1/.Trash-1000/files/orphan1

(orphan2 from disk2 not shown, since it wasn't selected)

## Scenario 6: `--size` alone → warning + orphan output

Given:
    $ touch ~/.local/share/Trash/files/orphan1

When:
    $ trash-list --show-non-trashinfo --size

Then stderr contains:
    trash-list: --size is ignored when --show-non-trashinfo is used

And stdout is exactly:
    /home/user/.local/share/Trash/files/orphan1

## Scenario 7: `--files` alone → warning + orphan output

Given:
    $ touch ~/.local/share/Trash/files/orphan1

When:
    $ trash-list --show-non-trashinfo --files

Then stderr contains:
    trash-list: --files is ignored when --show-non-trashinfo is used

And stdout is exactly:
    /home/user/.local/share/Trash/files/orphan1

## Scenario 8: `--files --size` together → combined, alphabetical warning

Given:
    $ touch ~/.local/share/Trash/files/orphan1

When:
    $ trash-list --show-non-trashinfo --files --size

Then stderr contains:
    trash-list: --files and --size are ignored when --show-non-trashinfo is used

And stdout is exactly:
    /home/user/.local/share/Trash/files/orphan1

## Scenario 9: `--size --files` (swapped argv order) → identical warning text

Given:
    $ touch ~/.local/share/Trash/files/orphan1

When:
    $ trash-list --show-non-trashinfo --size --files

Then stderr contains:
    trash-list: --files and --size are ignored when --show-non-trashinfo is used

(same warning as Scenario 8, even though `--size` was typed before `--files` — the
warning order is independent of argv order)
