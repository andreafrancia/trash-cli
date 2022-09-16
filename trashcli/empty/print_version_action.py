from trashcli.trash import print_version


class PrintVersionAction:
    def __init__(self, out, version, program_name):
        self.out = out
        self.version = version
        self.program_name = program_name

    def run_action(self, _parsed, _environ, _uid):
        print_version(self.out, self.program_name, self.version)
