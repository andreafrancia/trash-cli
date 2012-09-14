from textwrap import dedent
from nose.tools import assert_equals
import mock
from mock import Mock
from setup import BinDir

class TestMakeScript:
    def setUp(self):
        self.make_file_executable = Mock()
        self.write_file = Mock()
        self.make_dir = Mock()
        def capture(name, contents):
            self.name = name
            self.contents = contents
        self.write_file.side_effect = capture

        bindir = BinDir(
                make_file_executable = self.make_file_executable,
                write_file           = self.write_file,
                make_dir             = self.make_dir)
        bindir.add_script('trash-put', 'trashcli.cmds', 'put')

    def test_should_make_bin_dir(self):
        self.make_dir.assert_called_with('bin')

    def test_should_set_executable_permission(self):
        self.make_file_executable.assert_called_with('bin/trash-put')

    def test_should_write_the_script(self):
        self.write_file.assert_called_with( 'bin/trash-put', mock.ANY)

    def test_the_script_should_call_the_right_function_from_the_right_module(self):
        args, kwargs = self.write_file.call_args
        (_, contents) = args
        expected = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from trashcli.cmds import put as main
            sys.exit(main())
            """)
        assert_equals(expected, contents,
                      "Expected:\n---\n%s---\n"
                      "Actual  :\n---\n%s---\n"
                      % (expected, contents))

class TestListOfCreatedScripts:
    def setUp(self):
        self.bindir = BinDir(
                make_file_executable = Mock(),
                write_file           = Mock(),
                make_dir             = Mock())

    def test_is_empty_on_start_up(self):
        assert_equals(self.bindir.created_scripts, [])

    def test_collect_added_script(self):
        self.bindir.add_script('foo-command', 'foo-module', 'main')
        assert_equals(self.bindir.created_scripts, ['bin/foo-command'])
