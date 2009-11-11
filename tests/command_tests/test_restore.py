#!/usr/bin/python
# tests/command_tests/test_restore.py: Tests for the trash-restore command.
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

# Peraphs TODO: Refactoring: move cmd(), create_file(), trash(), trash-dir to
# a Sandbox class.
class RestoreTest(TestCase):
    def setUp(self):
        from common import create_cmdenv
        self.cmdenv = create_cmdenv()

        self.sandbox = Path("./sandbox").absolute()
        self.sandbox.remove()
        self.sandbox.mkdirs()
        self.trashdir = HomeTrashDirectory(
            Path('./sandbox/home/.local/share/Trash'))

    def create_file(self, path, content=None):
        """
        Create a file in sandbox with content
        """
        file=self.sandbox.join(path)
        file.touch()
        if content!=None :
            file.write_file(content)

        return file

    def trash(self, path):
        """
        Trash the file in the trash dir at sandbox/home/.local/share/Trash
        """
        result = self.trashdir.trash(path)

        # sanity check
        assert not path.exists()
        return result

    def test_version_option(self):
        """
        $ trash-restore --version
        0.2.1
        """
        raise SkipTest("trash-restore not yet ready")
        import re
        result = self.cmdenv.run('trash-restore','--version').assert_succeed()
        assert_equals("", result.err_data)
        expected = re.compile("trash-restore (\d)+\.(\d)+\.(\d)+")
        assert expected.match(result.out_data) is not None

    def test_restore_restores_trashed_file_absolute(self):
        from time import sleep
        """
        $ trash-list
        2009-01-12 12:00:00 /home/andrea/file
        1977-01-12 12:00:00 /home/andrea/file
        $ trash-restore /home/andrea/file # restore the latest trashed one
        $ trash-list
        1977-01-12 12:00:00 /home/andrea/file # the oldest remain in trashcan
        """
        raise SkipTest("trash-restore not yet ready")

        # prepare
        foo_file = self.create_file('foo', "first")
        trashed_file1 = self.trash(foo_file)

        sleep(1) # to make sure that deletion dates differs
        foo_file = self.create_file('foo', "second")
        trashed_file2 = self.trash(foo_file)

        sleep(1) # to make sure that deletion dates differs
        foo_file = self.create_file('foo', "latest")
        trashed_file3 = self.trash(foo_file)
        assert_false(foo_file.exists())

        print trashed_file1.deletion_date
        print trashed_file2.deletion_date
        print trashed_file3.deletion_date

        # execute
        self.cmd("trash-restore",foo_file.absolute()).assert_succeed()
        assert_true(foo_file.exists()) # File has been restored ?
        assert_equals("latest", foo_file.read()) # Is the latest deleted file?

    def test_restores_with_relative_name(self):
        """
        $ trash-list
        2009-01-12 12:00:00 /home/andrea/file
        $ cd /home/andrea
        $ trash-restore ./file
        """
        raise SkipTest("trash-restore not yet ready")

        # prepare
        foo_file = self.create_file('file', "content")
        self.trash(foo_file)
        assert_false(foo_file.exists())

        # execute
        self.cmdenv.run("trash-restore","./sandbox/file").assert_succeed()
        assert_true(foo_file.exists()) # File has been restored ?
        assert_equals("content", foo_file.read()) # Is the latest deleted file?

    def test_trashed_file_does_not_found(self):
        """
        $ trash-restore non-existent
        trash-restore: cannot restore path `non-existent': "
                      "Not found in any trash directory.
        """
        raise SkipTest()
        # execute
        result = self.cmd(self.restore_cmd, 'non-existent').assert_fail()
        # test
        assert_equals(result.exit_code, 1)
        assert_equals(result.out_data, "")
        assert_equals(result.err_data,
                      "trash-restore: cannot restore path `non-existent': "
                      "Not found in any trash directory.")

    def test_overwrite_attempt(self):
        """
        $ touch file
        $ trash-restore file
        trash-restore: cannot overwrite `file': File exists.
        """
        raise SkipTest()
        # prepare
        self.create_file('existing-file')
        self.trash('existing-file')
        self.create_file('existing-file')

        # execute
        result = self.cmdenv.run('trash-restore', 'existing-file').assert_fail()

        # test
        assert_equals(result.exit_code, 1)
        assert_equals(result.out_data, "")
        assert_equals(result.err_data,
                      "trash-restore: cannot overwrite`existing-file': "
                      "File exists.")

    def test_overwrite_attempt_with_force_option(self):
        """
        $ touch file
        $ trash-restore --force file     #succeed
        """
        raise SkipTest()
        # prepare
        self.create_file('existing-file')
        self.trash('existing-file')
        self.create_file('existing-file')

        # execute
        result = self.cmdenv.run('trash-restore', '--force',
                                 'existing-file').assert_succeed

        # test
        assert_equals(result.exit_code, 0)
        assert_equals(result.out_data, "")
        assert_equals(result.err_data, "")


    def test_help_option(self):
        """
        $ trash-restore --help
        Usage: trash-restore ...
        ...
        """
        raise SkipTest()
        result = self.cmdenv.run('trash-restore', '--help').assert_succeed()
        assert_equals(result.exit_code, 0)
        assert_equals(result.out_data,
"""Usage: trash-restore TRASHED-FILE [NEW-LOCATION]
Restore the TRASHED-FILE to its original location or to NEW-LOCATION.

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -f, --force          force overwrite
  -v, --verbose        explain what is being done
""")
        assert_equals(result.err_data, "")

    def test_issue_19(self):
        # bug: http://code.google.com/p/trash-cli/issues/detail?id=19
        # also reported in:
        #     https://bugs.launchpad.net/ubuntu/+source/trash-cli/+bug/310088

        self.sandbox.join('dir').mkdir()
        self.sandbox.join("dir/file").touch()

        self.trash(Path('sandbox/dir/file'))
        self.sandbox.join('dir').remove()

        result=self.cmdenv.cmd('restore-trash').run("0")
        result.assert_result(
            exit_code=0,
            error=""
        )

        assert_true(self.sandbox.child("dir").child("file").exists())

    def test_overwrite(self):
        # Trash a file, then create a file of the same name in its place.
        # Restore the file, and ensure that it asks before overwriting.
        self.sandbox.join('testfile').touch()
        self.trash(Path('sandbox/testfile'))
        self.sandbox.join('testfile').touch()
        result = self.cmdenv.cmd('restore-trash').run('0')
        result.assert_result(
            exit_code=1,
            error='Refusing to overwrite existing file "testfile".\n',
        )

