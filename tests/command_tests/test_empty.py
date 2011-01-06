#!/usr/bin/python
#
# tests/command_tests/test_empty.py: Tests for the trash-empty command.
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

class TestEmptyCommand(TestCase):
    """
    Tests for the trash-empty command
    """

    def setUp(self):
        from common import create_cmdenv
        self.cmdenv = create_cmdenv()

    def test_help_option(self):
        "$ trash-empty --help"

        self.cmdenv.run(
            "trash-empty", "--help"
            ).assert_result(
                exit_code=0,
                output=
"""Usage: trash-empty [days]

Purge trashed files.

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""",
                error="")

