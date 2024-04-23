from tests.support.help.help_reformatting import reformat_help_message, split_paragraphs


class TestParseHelp:
    def test_format_help_message(self):
        assert reformat_help_message(self.help_message) == (
            'usage: trash-list [-h] [--print-completion {bash,zsh,tcsh}] [--version] '
            '[--volumes] [--trash-dirs] [--trash-dir TRASH_DIRS] '
            '[--all-users]\n'
            '\n'
            'List trashed files\n'
            '\n'
            'options:\n'
            '  -h, --help            show this help message and exit\n'
            '  --print-completion {bash,zsh,tcsh}\n'
            '                        print shell completion script\n'
            "  --version             show program's version number and exit\n"
            '  --volumes             list volumes\n'
            '  --trash-dirs          list trash dirs\n'
            '  --trash-dir TRASH_DIRS\n'
            '                        specify the trash directory to use\n'
            '  --all-users           list trashcans of all the users\n'
            '\n'
            'Report bugs to https://github.com/andreafrancia/trash-cli/issues\n')

    def test_first(self):
        assert split_paragraphs(self.help_message)[0] == (
            'usage: trash-list [-h] [--print-completion {bash,zsh,tcsh}] [--version]\n'
            '                  [--volumes] [--trash-dirs] [--trash-dir TRASH_DIRS]\n'
            '                  [--all-users]\n')

    def test_second(self):
        assert split_paragraphs(self.help_message)[1] == (
            'List trashed files\n')

    def test_third(self):
        assert split_paragraphs(self.help_message)[2] == (
            'options:\n'
            '  -h, --help            show this help message and exit\n'
            '  --print-completion {bash,zsh,tcsh}\n'
            '                        print shell completion script\n'
            "  --version             show program's version number and exit\n"
            '  --volumes             list volumes\n'
            '  --trash-dirs          list trash dirs\n'
            '  --trash-dir TRASH_DIRS\n'
            '                        specify the trash directory to use\n'
            '  --all-users           list trashcans of all the users\n')

    def test_fourth(self):
        assert split_paragraphs(self.help_message)[3] == (
            'Report bugs to https://github.com/andreafrancia/trash-cli/issues\n'
        )

    def test_only_four(self):
        assert len(split_paragraphs(self.help_message)) == 4

    help_message = """\
usage: trash-list [-h] [--print-completion {bash,zsh,tcsh}] [--version]
                  [--volumes] [--trash-dirs] [--trash-dir TRASH_DIRS]
                  [--all-users]

List trashed files

options:
  -h, --help            show this help message and exit
  --print-completion {bash,zsh,tcsh}
                        print shell completion script
  --version             show program's version number and exit
  --volumes             list volumes
  --trash-dirs          list trash dirs
  --trash-dir TRASH_DIRS
                        specify the trash directory to use
  --all-users           list trashcans of all the users

Report bugs to https://github.com/andreafrancia/trash-cli/issues
"""
