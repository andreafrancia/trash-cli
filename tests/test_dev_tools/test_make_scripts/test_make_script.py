from textwrap import dedent

from tests.support import py2mock as mock
from tests.support.py2mock import Mock

from tests.support.make_scripts import Scripts
from tests.support.make_scripts import script_path_for


class TestMakeScript:
    def setup_method(self):
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
