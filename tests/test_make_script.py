import unittest
from textwrap import dedent

import mock
from mock import Mock
from scripts.make_scripts import (
    Scripts,
    script_path_for,
    script_path_without_base_dir_for,
)


class TestMakeScript(unittest.TestCase):
    def setUp(self):
        self.make_file_executable = Mock()
        self.write_file = Mock()

        def capture(name, contents):
            self.name = name
            self.contents = contents

        self.write_file.side_effect = capture

        bindir = Scripts(
            make_file_executable=self.make_file_executable,
            write_file=self.write_file)
        bindir.add_script('trash-put', 'trashcli_module', 'put')

    def test_should_set_executable_permission(self):
        self.make_file_executable.assert_called_with(script_path_for('trash-put'))

    def test_should_write_the_script(self):
        self.write_file.assert_called_with(script_path_for('trash-put'),
                                           mock.ANY)

    def test_the_script_should_call_the_right_function_from_the_right_module(self):
        args, kwargs = self.write_file.call_args
        (_, contents) = args
        expected = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from trashcli_module import put as main
            sys.exit(main())
            """)
        assert expected == contents, ("Expected:\n---\n%s---\n"
                                      "Actual  :\n---\n%s---\n"
                                      % (expected, contents))


class TestListOfCreatedScripts(unittest.TestCase):
    def setUp(self):
        self.bindir = Scripts(
            make_file_executable=Mock(),
            write_file=Mock())

    def test_is_empty_on_start_up(self):
        assert self.bindir.created_scripts == []

    def test_collect_added_script(self):
        self.bindir.add_script('foo-command', 'foo-module', 'main')
        assert self.bindir.created_scripts == [
            script_path_without_base_dir_for('foo-command')]
