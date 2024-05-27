from textwrap import dedent

from tests.support.make_scripts import Scripts
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.path import Path


class TestMakeScript:
    def setup_method(self):
        self.fake_fs = FakeFs()
        bindir = Scripts(self.fake_fs, Path("root"))

        self.fake_fs.mkdir("root")
        bindir.add_script('trash-put', 'trashcli_module', 'put')

    def test_should_set_executable_permission(self):
        assert self.fake_fs.is_executable("root/trash-put") == True

    def test_should_write_the_script(self):
        contents = self.fake_fs.read_text("root/trash-put")
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
