# Todo: `trash-list --orphans`

See `scenarios.md` for the full acceptance scenarios this checklist implements.

Process: for each item, write the test (red) -> minimal implementation change (green)
-> run full `pytest` suite -> only if green, commit -> check off the item in this file
as part of that same commit. Never move to the next item with a failing test. Never
commit on red.

- [x] 0. Parser groundwork: `--orphans` flag + `ListTrashArgs` field +
      parser tests + updated `--help` text.
- [x] 1. Scenario 1 (happy path): exclusive orphan listing branch in
      `ListTrash.list_all_trash` + `FakeTrashDir.add_orphan` helper + new test file.
- [x] 2. Scenario 4: regression guard (flag absent -> orphan invisible).
- [x] 3. Scenario 2: no orphans -> empty output.
- [x] 4. Scenario 3: multiple orphans.
- [x] 5. Scenario 5: respects `--trash-dir` scoping.
- [ ] 6. Scenario 6: `--size` alone -> warning.
- [ ] 7. Scenario 7: `--files` alone -> warning.
- [ ] 8. Scenario 8: `--files --size` combined -> alphabetical warning.
- [ ] 9. Scenario 9: swapped argv order -> identical warning text.
- [ ] 10. Docs: `man/man1/trash-list.1` OPTIONS + EXAMPLES entry.
