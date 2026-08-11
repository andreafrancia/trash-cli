# Security review — release automation changes

Date: 2026-08-11
Scope: `.github/workflows/bump-version.yml`, `.github/workflows/publish-release.yml`,
and the removal of `make-release.yml` / `docs/how-to-build-and-upload-a-new-release.rst`
(see `RELEASE-AUTOMATION.md` for what these changes are and why).

Method: ran the `security-review` methodology — a sub-agent identified candidate
vulnerabilities, then a separate sub-agent per candidate applied a strict false-positive
filter (repo-write-access prerequisites, concreteness of attack path, actual privilege
escalation vs. redundant capability). Only findings scoring >= 8/10 confidence from the
filtering pass would have been reported.

## Result: no high-confidence vulnerabilities

Two candidates were investigated and empirically tested (not just reasoned about), both
filtered out:

| Candidate | Where | Verdict | Confidence |
|---|---|---|---|
| Unescaped `${{ github.event.release.tag_name }}` interpolated into a `run:` shell command | `publish-release.yml:37` (`gh release upload`) | Filtered — mechanism is real (verified: git tag names can contain `$()`/backticks, and GitHub Actions does literal text substitution into `run:` blocks with no escaping — a tag like `` v1.2.3$(touch${IFS}/tmp/PWNED) `` triggers real command execution), but it grants no capability the attacker doesn't already have: whoever can create that tag already fully controls the commit being built, and can plant the same payload directly in `setup.py`/`pyproject.toml` with no injection needed. Requires pre-existing repo Write access either way. | 3/10 |
| Same pattern via `${{ github.ref_name }}` | `bump-version.yml:39` (`git push`) | Filtered — same mechanism, but `workflow_dispatch` itself requires Write access to invoke, and the only effect is a commit+tag pushed to the repo the attacker could already push to directly. | 2/10 |

Both were technically-real injection primitives with no privilege escalation behind
them — this repo's threat model already assumes Write-access collaborators are
trusted, and neither workflow is reachable by `pull_request` or any other
untrusted-triggerable event, so there's no path from an external/anonymous actor into
either bug.

The core design decisions from the release-automation work hold up under this review:
no `pull_request` trigger anywhere near the publish path, minimal/scoped `permissions:`
blocks per job, OIDC Trusted Publishing instead of a stored PyPI secret, and a
required-reviewer + tag-pattern gate on the `pypi` environment.

## Additional hints (below the strict "confirmed vuln" bar, worth doing anyway)

- **Pin `pypa/gh-action-pypi-publish@release/v1` to a commit SHA**, not the floating
  branch. It's the one job in this whole pipeline holding `id-token: write` and
  actually talking to PyPI — the highest-trust step deserves the tightest
  supply-chain pinning, even though "unpinned action" wasn't in scope for the
  strict vuln report.
- **`bump-version.yml` installs the entire dev toolchain** (`pytest`, `mypy`,
  `twine`, `tox`, `build`, `PyYAML`, …) via `scripts/lib/install-python-requirements`,
  even though `scripts/bump` only touches one file and needs almost none of it.
  Trimming this shrinks the set of third-party code that runs (with a
  `contents: write` token live in the environment) for no functional benefit.
- **Both `run:` interpolations flagged above are still worth fixing on general
  principle**, independent of today's exploitability: pass `github.ref_name` /
  `tag_name` through an `env:` var and reference it as `"$TAGNAME"` inside the
  script instead of `${{ }}`-interpolating directly into shell text. Costs nothing,
  and removes the injection primitive entirely so it's not sitting there waiting
  for the trust model to change (e.g. if a second collaborator is ever added).
- **The `pypi` environment's required-reviewer gate has `can_admins_bypass: true`**,
  and the repo admin is also the sole required reviewer — worth being clear-eyed
  that this gate is a deliberate-click safeguard against mistakes, not a control
  against account compromise. The real backstop is 2FA on the GitHub and PyPI
  accounts.
