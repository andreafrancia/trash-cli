from trashcli.fstab.protocols.df_command import DfCommand


class FakeDfCommand(DfCommand):
    def __init__(self):
        self.output = ''

    def set_output(self, output):  # type: (str) -> None
        self.output = output

    def df_output(self):  # type: () -> str
        return self.output
