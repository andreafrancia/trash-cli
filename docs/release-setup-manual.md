Release pipeline: one-time website setup
=========================================

This is a runbook for the manual, one-time configuration that has to exist
on pypi.org and github.com before the automated release pipeline (see
``AGENTS.md`` -> "Release process") can publish to PyPI. Follow it cold, no
other context needed.

There are two independent pieces. As of 2026-08-10, the GitHub side is
already done (see "Verifying" below to confirm it's still in place); the
PyPI side still needs to be done by hand, since it requires logging into
pypi.org and nothing here has access to that account.

1. PyPI: register a Trusted Publisher
--------------------------------------

This tells PyPI to accept an upload from this specific GitHub workflow
without any password or API token.

1. Log in to https://pypi.org with the account that owns the ``trash-cli``
   project.
2. Go to https://pypi.org/manage/project/trash-cli/settings/publishing/
3. Under "Trusted Publisher Management", click "Add a new publisher" and
   choose GitHub.
4. Fill in exactly:

   - **Owner**: ``andreafrancia``
   - **Repository name**: ``trash-cli``
   - **Workflow name**: ``publish-release.yml``
   - **Environment name**: ``pypi``

5. Save.

Nothing else is needed on the PyPI side — no API token, no secret to copy
anywhere.

2. GitHub: the ``pypi`` Environment
-------------------------------------

This makes the PyPI-publish job in ``publish-release.yml`` pause for your
approval, and restricts which tags are even allowed to reach it. Already
created — these are the steps to redo it if it's ever deleted, or to audit
what's there.

1. Go to https://github.com/andreafrancia/trash-cli/settings/environments
2. If ``pypi`` doesn't exist: click "New environment", name it ``pypi``,
   click "Configure environment".
3. Under "Deployment protection rules", enable "Required reviewers" and add
   ``andreafrancia``.
4. Under "Deployment branches and tags", choose "Selected branches and tags",
   then "Add deployment tag rule" with the pattern:

   ::

       0.[0-9]*.[0-9]*.[0-9]*

   This matches release tags like ``0.24.8.10`` and rejects anything else
   (branch names, arbitrary tags).
5. Save.

Verifying both sides
---------------------

PyPI side — open
https://pypi.org/manage/project/trash-cli/settings/publishing/ and confirm
a Trusted Publisher entry exists with owner ``andreafrancia``, repo
``trash-cli``, workflow ``publish-release.yml``, environment ``pypi``.

GitHub side — run:

.. code-block:: bash

    gh api repos/andreafrancia/trash-cli/environments/pypi \
      --jq '{name, reviewers: .protection_rules[] | select(.type=="required_reviewers") | .reviewers[].reviewer.login}'
    gh api repos/andreafrancia/trash-cli/environments/pypi/deployment-branch-policies \
      --jq '.branch_policies[] | {name, type}'

Expect the reviewer to be ``andreafrancia`` and the tag policy to be
``0.[0-9]*.[0-9]*.[0-9]*``.

Once both are confirmed, the three-step release process in ``AGENTS.md`` is
fully wired up: bump the version, publish a GitHub Release on the new tag,
approve the pending deployment, done.
