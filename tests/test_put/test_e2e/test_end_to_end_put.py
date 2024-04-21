# Copyright (C) 2021 Andrea Francia Bereguardo(PV) Italy
from textwrap import dedent

import pytest

from tests.support.run_command import temp_dir  # noqa
from tests.support.my_path import MyPath
from tests.test_put.test_e2e.run_trash_put import run_trash_put
from trashcli.lib.exit_codes import EX_IOERR


@pytest.mark.slow
class TestEndToEndPut:
    def setup_method(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_last_line_of_help(self, temp_dir):
        result = run_trash_put(temp_dir, ['--help'])

        assert result.stdout.last_line() == \
               'Report bugs to https://github.com/andreafrancia/trash-cli/issues'

    def test_without_args(self, temp_dir):
        result = run_trash_put(temp_dir, [])

        assert ([result.stderr.first_line(), result.exit_code] ==
                ['usage: trash-put [OPTION]... FILE...', 2])

    def test_wrong_option(self, temp_dir):
        result = run_trash_put(temp_dir, ['--wrong-option'])

        assert [result.stderr.last_line(),
                result.exit_code] == \
               ['trash-put: error: unrecognized arguments: --wrong-option', 2]

    def test_on_help(self, temp_dir):
        result = run_trash_put(temp_dir, ['--help'])

        assert [result.help_message(),
                result.exit_code] == \
               [dedent('''\
                usage: trash-put [OPTION]... FILE...

                Put files in trash

                positional arguments:
                  files

                options:
                  -h, --help            show this help message and exit
                  --print-completion {bash,zsh,tcsh}
                                        print shell completion script
                  -d, --directory       ignored (for GNU rm compatibility)
                  -f, --force           silently ignore nonexistent files
                  -i, --interactive     prompt before every removal
                  -r, -R, --recursive   ignored (for GNU rm compatibility)
                  --trash-dir TRASHDIR  use TRASHDIR as trash folder
                  -v, --verbose         explain what is being done
                  --version             show program's version number and exit

                all trash-cli commands:
                  trash-put             trash files and directories.
                  trash-empty           empty the trashcan(s).
                  trash-list            list trashed files.
                  trash-restore         restore a trashed file.
                  trash-rm              remove individual files from the trashcan
  
                To remove a file whose name starts with a '-', for example '-foo',
                use one of these commands:

                    trash -- -foo

                    trash ./-foo

                Report bugs to https://github.com/andreafrancia/trash-cli/issues
            '''), 0]

    def test_it_should_skip_dot_entry(self, temp_dir):
        result = run_trash_put(temp_dir, ['.'])

        assert result.combined() == \
               ["trash-put: cannot trash directory '.'\n", EX_IOERR]

    def test_it_should_skip_dotdot_entry(self, temp_dir):
        result = run_trash_put(temp_dir, ['..'])

        assert result.combined() == \
               ["trash-put: cannot trash directory '..'\n", EX_IOERR]

    def test_it_should_print_usage_on_no_argument(self, temp_dir):
        result = run_trash_put(temp_dir, [])

        assert result.combined() == \
               ['usage: trash-put [OPTION]... FILE...\n'
                'trash-put: error: Please specify the files to trash.\n', 2]

    def test_it_should_skip_missing_files(self, temp_dir):
        result = run_trash_put(temp_dir,
                               ['-f', 'this_file_does_not_exist',
                                'nor_does_this_file'])
        assert result.combined() == ['', 0]
