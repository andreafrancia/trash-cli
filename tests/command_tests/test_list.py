#!/usr/bin/python
# tests/command_tests/test_put.py: Tests for the trash-put command.
#
# Copyright (C) 2009 Andrea Francia Trivolzio(PV) Italy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from unittest import TestCase
from trashcli.filesystem import Path
from trashcli.trash import HomeTrashDirectory
from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.tools import assert_true
from nose.tools import assert_false
from nose.tools import raises
from nose import SkipTest
from cmd import Command
from cmd import CommandEnviroment

class Test(TestCase):

    def setUp(self):
        import trashcli
        cmds_aliases={}
        scripts_dir=Path(trashcli.__file__).parent.parent.join("scripts")
        for i in ["trash-list", "trash-put", "trash-empty"]:
            command=scripts_dir.join(i)
            if not command.exists():
                raise SkipTest("Script not found, please use 'setup.py develop --scripts-dir scripts': %s" % command)
            else:
                cmds_aliases[i]=command

        self.cmdenv=CommandEnviroment(cmds_aliases,"./sandbox", {})

    def test_help_option(self):
        "$ trash-list --help"

        self.cmdenv.run("trash-list", "--help").assert_result(
            exit_code=0,
            output=
"""Usage: trash-list

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""",
            error="")


