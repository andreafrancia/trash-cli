---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---
**Describe the bug**
A clear and concise description of what the bug is.

**trash-cli version**
Output of: trash-put --version

**Are you using the latest version of trash-cli?**
Yes/no

**Have you tried if the bug is present in the latest version of trash-cli?**
Yes/no

**Please, install the latest version of trash-cli and try again before submitting the bug**

First of all you need to uninstall any previous version of trash-cli::

    $ [sudo] pip uninstall trash-cli # remove the previous version (with pip)
    $ [sudo] apt-get remove trash-cli # remove the previous version (with apt)
    $ [sudo] yum uninstall trash-cli # remove the previous version (with yum)
    $ ... # refer to the package manager of your distribution

Then install the latest version from git::

    $ pip install pip install git+https://github.com/andreafrancia/trash-cli

Have done that? Then continue with the bug report.

**Operating system:**
 - OS: [e.g. Debian, Ubuntu, Fedora, macOs, Cygwin]

**To Reproduce**
Copy and paste the commands (and their output) to execute in order to reproduce 
the behavior:

$ touch foo
$ trash-put foo
$ ls foo
ls: cannot access 'foo': No such file or directory
$ trash-list
2020-12-13 18:36:21 /Users/andrea/trash-cli/foo

**Expected behavior**
A clear and concise description of what you expected to happen.

**Volumes detail**
If your issue is related to recognition of volumes, please provide the output 
of: `trash-list --debug-volumes` 
