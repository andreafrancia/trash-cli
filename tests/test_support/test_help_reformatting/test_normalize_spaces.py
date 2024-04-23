from tests.support.help.help_reformatting import normalize_spaces


class TestNormalizeSpaces:
    def test(self):
        text = """usage: trash-list [-h] [--print-completion {bash,zsh,tcsh}] [--version]
                  [--volumes] [--trash-dirs] [--trash-dir TRASH_DIRS]
                  [--all-users]"""

        assert normalize_spaces(text) == (
            "usage: trash-list [-h] [--print-completion {bash,zsh,tcsh}] "
            "[--version] [--volumes] [--trash-dirs] [--trash-dir TRASH_DIRS] "
            "[--all-users]")
