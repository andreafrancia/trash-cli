# Release automation — story tracker

Goal: fewer manual commands, a real downloadable GitHub Release with the
sdist attached, and PyPI publishing that never requires a secret stored in
GitHub and can never be triggered by approving a fork PR's workflow run.

## Decisions (2026-08-10)

Each entry: the question, what was decided, why, and what was considered but
not chosen.

**Version bump trigger.** Decided: a manual `workflow_dispatch` workflow
(`bump-version.yml`) that computes the version, commits, tags, and pushes.
Why: removes the local `scripts/bump` + `git push` step entirely — you
trigger it from the Actions tab and nothing runs on your machine.
Considered and rejected: keeping `scripts/bump` local and only automating
what happens after the tag is pushed — rejected because it still requires a
local command every release, which is exactly what "fewer commands" was
asking to remove.

**Build+publish trigger.** Decided: publishing a GitHub Release through the
web UI (`release: published` event), on the tag the bump workflow created.
Why: this is the one release-time action that's inherently manual anyway
(writing release notes), so it doubles as the trigger — no separate "kick off
the pipeline" step. Considered and rejected: triggering on tag push directly
— would fire before you've had a chance to write release notes, and
conflates "a tag exists" with "I want to ship this."

**PyPI publishing mechanism.** Decided: PyPI Trusted Publishing (OIDC-based
— GitHub proves its identity to PyPI per run via a short-lived token; no API
token or password stored in GitHub at all). Why: this directly answers the
original concern — there is no secret in GitHub that could leak or be
misused, because there is no secret. Considered and rejected: a PyPI API
token stored as a GitHub Actions secret — works, but is exactly the kind of
long-lived credential that can be exfiltrated by a malicious workflow change
or a compromised Action; Trusted Publishing removes that risk class
entirely rather than mitigating it.

**Gating the PyPI publish.** Decided: the `publish-pypi` job runs under a
GitHub Environment (`pypi`) with a required-reviewer protection rule, so
every publish needs an explicit human approval click, plus a deployment tag
policy (`0.[0-9]*.[0-9]*.[0-9]*`) so only version-shaped tags can even reach
that environment. Why: two independent layers — even if the trigger design
changes later, a human still has to approve the specific PyPI-touching job,
and even an approved run can't publish from an unexpected ref.

**Keeping "approve workflow run" out of the PyPI path.** Decided: neither
`bump-version.yml` nor `publish-release.yml` is ever triggered by
`pull_request`. Why: GitHub's "approve and run workflow" button (used to let
first-time/fork contributors' CI run) only exists for `pull_request`-triggered
runs. Since the PyPI-publishing job isn't reachable from that trigger type at
all, there is no code path from "I approved a stranger's PR to run CI" to "a
release got published to PyPI" — this was the original worry driving the
whole approval-safety question, and it's solved structurally rather than by
a setting that could be misconfigured later.

**TestPyPI step.** Decided: dropped from the automated flow. Why: its only
real value — confirming the sdist actually installs and the CLI runs — is
already covered by `run-tests.yml`'s existing `sdist` job on every push,
before a release is ever drafted. Keeping it would have added a second
Trusted Publisher + upload step for no new coverage.

**Old `make-release.yml`.** Decided: deleted rather than repurposed. Why: it
ran on every push to every branch and only uploaded a dev-version CI
artifact nobody downloaded — fully redundant with `run-tests.yml`'s `sdist`
job, which does the same build/install check without the misleading name.

**Tag format.** Decided: kept the existing bare version string (e.g.
`0.24.8.10`, no `v` prefix) rather than switching conventions. Why: matches
every existing tag in the repo's history; no reason to break that for
tooling that doesn't require a prefix.

**GitHub Environment created immediately vs. left as a manual step.**
Decided: created via `gh api` during this session (with explicit go-ahead),
rather than deferred entirely to the Story 8 manual. Why: it's a repo
setting, not a file — nothing to commit, and doing it once now means Story 5
is only blocked on the one piece that genuinely requires your own pypi.org
login. Considered and rejected: leaving both halves of Story 5 for later —
would have meant redoing analysis/parameters (user id, tag pattern syntax)
from scratch in a future session.

**Push policy for this session's work.** Decided: everything stayed
committed locally on `release`, nothing pushed to `origin`. Why: explicit
instruction — workflow files and process changes going live unattended,
while you're stepping away, wasn't something to do without a review pass
first.

Status legend: `[ ]` todo, `[~]` implemented and locally verified but the
story's own live/on-GitHub test hasn't run yet (everything so far is
committed locally, not pushed), `[x]` fully done including the live test.

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

## [~] Story 2 — `bump-version.yml`: manual workflow to bump + tag + push

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

## [~] Story 3 — Delete the redundant `make-release.yml`

It runs on every push to every branch and only duplicates what the `sdist`
job in `run-tests.yml` already checks, uploading a dev-version tarball nobody
downloads.

**Implementation:** `git rm .github/workflows/make-release.yml`.

**How to test after implementing:** push a commit to any branch and confirm
in the Actions tab that only `run-tests.yml` runs (no "Make Release" run
appears), and its `sdist` job still passes.

**Definition of done:** file removed, CI still green on push/PR.

---

## [~] Story 4 — `publish-release.yml`: build sdist and attach to the Release

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

## [~] Story 5 — One-time setup: PyPI Trusted Publisher + `pypi` Environment

Manual configuration, not a code change.

**Steps:**
1. ~~On https://pypi.org/manage/project/trash-cli/settings/publishing/ , add a
   Trusted Publisher: owner `andreafrancia`, repo `trash-cli`, workflow
   `publish-release.yml`, environment name `pypi`.~~ **Still to do by Andrea**
   — requires your pypi.org login, no tool here has access to it.
2. ~~On GitHub: Settings -> Environments -> New environment -> name it `pypi`.
   Add a "Required reviewers" protection rule with Andrea as reviewer.
   Optionally add a deployment tag policy restricting it to tags matching the
   version pattern.~~ **Done 2026-08-10** via `gh api`: environment `pypi`
   created with required reviewer `andreafrancia`, and a tag-name deployment
   policy limited to `0.[0-9]*.[0-9]*.[0-9]*`.

**How it was verified (GitHub side):**
```
gh api repos/andreafrancia/trash-cli/environments/pypi
gh api repos/andreafrancia/trash-cli/environments/pypi/deployment-branch-policies
```
confirmed the `required_reviewers` rule lists `andreafrancia` and the tag
policy is `0.[0-9]*.[0-9]*.[0-9]*`.

**Still needed to close this story:** the PyPI Trusted Publisher entry (step
1) — do this via Story 8's manual, then re-check the "Publishing" settings
page on the PyPI project lists it.

**Definition of done:** both sides configured; no secret exists in GitHub
repo/org secrets for PyPI.

---

## [~] Story 6 — Gated `publish-pypi` job in `publish-release.yml`

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

## [x] Story 7 — Finalize AGENTS.md, retire the old manual doc

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

---

## [x] Story 8 — Write a manual for the one-time website setup

Story 5 is a terse checklist written for whoever's already deep in this
conversation's context. This story is a standalone, human-facing runbook you
can follow cold, months from now, without remembering any of this design
discussion.

**Implementation:** new file `docs/release-setup-manual.md`, written for a
human clicking through pypi.org and github.com, not for an LLM. Covers, in
order:
1. Creating the PyPI Trusted Publisher entry — exact URL
   (`https://pypi.org/manage/project/trash-cli/settings/publishing/`), exact
   field values (owner, repo, workflow filename, environment name).
2. Creating the GitHub `pypi` Environment — exact Settings path
   (repo -> Settings -> Environments -> New environment), exact field values
   (name, required reviewers, optional deployment tag policy).
3. How to verify both sides afterward (same checks as Story 5's "how to
   test": `gh api .../environments/pypi`, and the Publishing page on PyPI).

**How to test after implementing:** follow the document literally, with no
other context than what's written in it, and confirm each step lands on the
right settings page with the right fields — this is also how you'll actually
perform Story 5.

**Definition of done:** the manual is accurate against the current PyPI/
GitHub UI, and Story 5 can be executed from it alone.
