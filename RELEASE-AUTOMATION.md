# Release automation — story tracker

Goal: fewer manual commands, a real downloadable GitHub Release with the
sdist attached, and PyPI publishing that never requires a secret stored in
GitHub and can never be triggered by approving a fork PR's workflow run.

Design decided 2026-08-10:

- Trigger for version bump: manual `workflow_dispatch` (`bump-version.yml`) —
  no local commands needed.
- Trigger for build+publish: publishing a GitHub Release via the web UI
  (`release: published` event) on the tag created by the bump workflow.
- PyPI publishing: Trusted Publishing (OIDC, no stored secret), gated behind
  a GitHub Environment (`pypi`) with required reviewers. Neither new workflow
  is ever triggered by `pull_request`, so there is no path from "approve this
  PR's workflow run" to a PyPI publish.
- TestPyPI step dropped: `run-tests.yml`'s existing `sdist` job already
  builds, installs, and exercises the CLI on every push, which was TestPyPI's
  only real value here.

Each story below: implement -> verify using its "how to test" section ->
commit locally (no push) -> check the box.

---

## [x] Story 1 — Document current process in AGENTS.md

Baseline documentation of the process as it existed before automation.

**How it was tested:** cross-checked every claim in AGENTS.md's Versioning/
Release process sections against the actual scripts (`scripts/bump`,
`tests/support/tools/{bump_cmd,version_from_date,version_saver}.py`,
`setup.cfg`, `.github/workflows/*.yml`).

Commit: `0de3cf9`

---

## [ ] Story 2 — `bump-version.yml`: manual workflow to bump + tag + push

As Andrea, I want a manually-triggered workflow that computes today's
version, commits it, tags it, and pushes both, so I don't run anything
locally.

**Implementation:** `.github/workflows/bump-version.yml`, `workflow_dispatch`
trigger only, `permissions: contents: write`. Steps: checkout, set
`git config user.name/user.email` (needed since `scripts/bump` shells out to
`git commit`), run `scripts/bump`, `git tag "$(python -c '...' --version)"`,
`git push origin HEAD --follow-tags`.

**How to test after implementing (after you push this branch):**
1. Push a throwaway branch, e.g. `test-bump-workflow`.
2. `gh workflow run bump-version.yml --ref test-bump-workflow`.
3. `gh run watch` and confirm it succeeds.
4. `git fetch && git log origin/test-bump-workflow -1` — confirm a
   `Bump version to 'X'` commit exists, and `git tag -l` shows the new tag
   pointing at it.
5. Clean up: delete the test tag and branch both locally and on origin.

**Definition of done:** running the workflow against a ref produces a bump
commit and matching pushed tag with no local commands.

---

## [ ] Story 3 — Delete the redundant `make-release.yml`

It runs on every push to every branch and only duplicates what the `sdist`
job in `run-tests.yml` already checks, uploading a dev-version tarball nobody
downloads.

**Implementation:** `git rm .github/workflows/make-release.yml`.

**How to test after implementing:** push a commit to any branch and confirm
in the Actions tab that only `run-tests.yml` runs (no "Make Release" run
appears), and its `sdist` job still passes.

**Definition of done:** file removed, CI still green on push/PR.

---

## [ ] Story 4 — `publish-release.yml`: build sdist and attach to the Release

As Andrea, when I publish a GitHub Release for a tag, I want the sdist built
from that tag and attached as a downloadable asset automatically.

**Implementation:** `.github/workflows/publish-release.yml`, trigger
`on: release: types: [published]`, `permissions: contents: write` (to upload
the release asset). Job: checkout `${{ github.event.release.tag_name }}`,
`python -m build --sdist`, `twine check --strict dist/*.tar.gz`,
`gh release upload "${{ github.event.release.tag_name }}" dist/*.tar.gz`.

**How to test after implementing (after you push):**
1. Create a real tag on a harmless commit, e.g.
   `git tag test-release-workflow && git push origin test-release-workflow`.
2. `gh release create test-release-workflow --prerelease --notes "test"`.
3. Watch the workflow run; confirm it succeeds.
4. `gh release view test-release-workflow` — confirm the `.tar.gz` asset is
   attached and downloadable.
5. Clean up: `gh release delete test-release-workflow` and delete the tag
   locally and on origin.

**Definition of done:** publishing a Release attaches a working sdist within
a couple of minutes, no PyPI interaction yet.

---

## [ ] Story 5 — One-time setup: PyPI Trusted Publisher + `pypi` Environment

Manual configuration, not a code change — done by Andrea, not committed.

**Steps:**
1. On https://pypi.org/manage/project/trash-cli/settings/publishing/ , add a
   Trusted Publisher: owner `andreafrancia`, repo `trash-cli`, workflow
   `publish-release.yml`, environment name `pypi`.
2. On GitHub: Settings -> Environments -> New environment -> name it `pypi`.
   Add a "Required reviewers" protection rule with Andrea as reviewer.
   Optionally add a deployment tag policy restricting it to tags matching the
   version pattern.

**How to test after implementing:**
- `gh api repos/andreafrancia/trash-cli/environments/pypi` shows the
  environment with `protection_rules` containing a `required_reviewers` rule.
- The PyPI project's "Publishing" settings page lists the trusted publisher
  entry.

**Definition of done:** both sides configured; no secret exists in GitHub
repo/org secrets for PyPI.

---

## [ ] Story 6 — Gated `publish-pypi` job in `publish-release.yml`

As Andrea, after the sdist is built, I want a second job that publishes it to
PyPI, gated behind my approval, using OIDC only.

**Implementation:** add a `publish-pypi` job to `publish-release.yml`:
`needs: build`, `environment: pypi`, `permissions: id-token: write`,
downloads the `dist/` artifact from the `build` job, runs
`pypa/gh-action-pypi-publish@release/v1`. Depends on Story 5 being done first
(environment must exist before the job's first real run).

**How to test after implementing:** the real next release IS the test —
publish version `0.YY.M.D` for real:
1. Run `bump-version.yml`, draft+publish the GitHub Release on the new tag.
2. Confirm the workflow run pauses at "Review deployments" for the `pypi`
   environment.
3. Approve it.
4. Confirm the new version appears on https://pypi.org/project/trash-cli/
   within a few minutes, and `pip index versions trash-cli` shows it.

If you'd rather not risk a real PyPI upload on the first try, point Story 5's
Trusted Publisher + environment at TestPyPI first, run the same steps, then
redo Story 5 against real PyPI once confirmed.

**Definition of done:** a published Release results in a PyPI upload only
after explicit manual approval, with zero stored secrets involved.

---

## [ ] Story 7 — Finalize AGENTS.md, retire the old manual doc

**Implementation:** rewrite AGENTS.md's "Release process" section to describe
the final flow end-to-end (run `bump-version.yml` -> draft+publish a Release
on the new tag -> approve the `pypi` environment deployment). Replace
`docs/how-to-build-and-upload-a-new-release.rst` with a short pointer to
AGENTS.md, or delete it.

**How to test after implementing:** `grep -rn "how-to-build-and-upload"` the
repo to confirm nothing else links to the old doc; re-read AGENTS.md and
confirm it matches the workflow YAML files exactly (no drift).

**Definition of done:** one source of truth for the release process, and it's
accurate.
