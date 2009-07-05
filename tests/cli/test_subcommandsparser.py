#!/usr/bin/python
# tests/cli/test_subcommandsparser.py: Unit tests for trashcli.cli.subcommandsparser
#
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy
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

__author__ = "Andrea Francia (andrea.francia@users.sourceforge.net)"
__copyright__ = "Copyright (c) 2009 Andrea Francia"
__license__ = "GPL"

from __future__ import absolute_import
from unittest import TestCase
from nose.tools import assert_equals
from nose.tools import raises

from trashcli.cli.subcommandsparser import SubCommandsParser
from trashcli.cli.subcommandsparser import CommandNotFoundError
from trashcli.cli.subcommandsparser import CommandNotSpecifiedError

class SubCommandsParserTest(TestCase):

    def setup_parser(self):
        """
        setup the parser for tests.
        """

        parser = SubCommandsParser()

        command2=DummyCommand()
        parser.add_sub_command("command1", DummyCommand())
        parser.add_sub_command("command2", command2)
        parser.add_sub_command("command3", DummyCommand())

        return (parser, command2)

    def test_parse_returns_the_right_command_with_no_args(self):

        (parser, command2) = self.setup_parser()
        (selected_command, ignored_args) = parser.parse("command2")
        assert_same(command2, selected_command)

    def test_parse_returns_the_right_command_with_multiple_args(self):

        (parser, command2) = self.setup_parser()
        (selected_command, ignored_args) = parser.parse("command2", "arg1", "arg2")
        assert_same(command2, selected_command)

    @raises(CommandNotFoundError)
    def test_parse_raises_command_not_found_error(self):

        (parser, ignored) = self.setup_parser()
        parser.parse("non-existent-command")

    @raises(CommandNotSpecifiedError)
    def test_parse_raises_command_not_specified_error(self):

        (parser, ignored) = self.setup_parser()
        parser.parse() # no args

    class DummyCommand:
        pass

    def test_execute_run_the_specified_command

def assert_same(expected, actual):
    from nose.tools import assert_true

    assert_true(expected is actual)
