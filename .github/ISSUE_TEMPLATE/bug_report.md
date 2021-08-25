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

**Operating system:**
 - OS: [e.g. Debian, Ubuntu, Fedora, macOs, Cygwin]

**To Reproduce**
Copy and paste the commands (and their output) to execute in order to reproduce
the behavior:

$ touch foo
$ trash-put foo
$ ls foo
gls: cannot access 'foo': No such file or directory
$ trash-list
2020-12-13 18:36:21 /Users/andrea/trash-cli/foo

**Expected behavior**
A clear and concise description of what you expected to happen.
