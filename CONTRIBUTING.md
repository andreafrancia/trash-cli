# Contributing to `trash-cli`

Thanks for considering contributing to `trash-cli`! This document lists
the conventions and expectations for contributions to this project. For
environment setup, running tests, and coding/testing conventions, see
`DEVELOPMENT.md`.

## Where to Ask Questions

Questions and discussion happen on GitHub, through this repo's
[Issues](https://github.com/andreafrancia/trash-cli/issues) and
[Discussions](https://github.com/andreafrancia/trash-cli/discussions)
— there's no separate chat or mailing list.

## Code of Conduct

Be respectful and constructive in issues and PRs. Personal attacks or
harassment won't be tolerated.

## Reporting Bugs / Requesting Features

- Please search existing issues and discussions first, to avoid
  duplicates.
- Use the "Bug report" or "Feature request" issue templates on
  GitHub — they already prompt for the information that's normally
  needed (e.g. `trash-cli` version, steps to reproduce).

## One Outstanding PR per Contributor

- Please try to open only one outstanding PR at a time.
- If you have multiple outstanding PRs, please make clear which one I
  should review first.

## Duplicating Code

- You don't need to know how to avoid all the duplication in advance,
  you can add duplication and refactor later (but before submitting
  the PR).
- Before submitting a PR, check whether similar code already exists;
  reuse or extend it instead of duplicating.

## Use of AI Assistants

- You're welcome to use AI coding assistants to help write code, tests,
  or replies in this project. What matters is that you read,
  understand, and take responsibility for everything submitted under
  your name — treat AI output as a draft to review and edit, not a
  finished answer to paste in.
- Please curate review replies before posting them. Keep them focused
  and specific to the point being discussed; long, unfocused responses
  that look machine-generated and unedited make a review thread
  slower, not faster, for both sides.
- When asked for something simple and actionable in review — rebasing
  a branch, renaming a variable, splitting a commit — please just do
  it rather than relying on back-and-forth replies about it.
- I can only communicate with you, the contributor, not with any tool
  you use. If a reply doesn't address what was actually asked, I'll
  assume it wasn't reviewed before posting and will ask again or
  rephrase.
- If a PR stalls because review comments keep going unaddressed or
  replies don't engage with the actual feedback, I reserve the right
  to take the work as-is and finish it myself, or to set the PR aside.
  This isn't a penalty — it's just how I keep contributions from
  getting stuck indefinitely.

## Pull Request Checklist

- Keep the PR focused on one change; see "One Outstanding PR per
  Contributor" and "Duplicating Code" above.
- Rebase on top of `master` and keep history linear — no merge
  commits.
- Make sure `scripts/pre-push` passes (see `DEVELOPMENT.md`).
- Describe what the PR does and why in its description; link the
  issue it addresses, if there is one.

## Review Time Expectations

Reviews are done on a best-effort, volunteer basis. Most PRs get a
first response within a few days, but it can occasionally take a few
weeks depending on my availability. If you haven't heard back after
2 weeks, a friendly ping on the PR is welcome.

## License / Contribution Terms

The project is licensed under the GPL v2 (`COPYING`). By submitting a
pull request, you agree that your contribution is licensed under the
same license.
