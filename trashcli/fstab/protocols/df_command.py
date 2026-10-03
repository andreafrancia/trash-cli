from trashcli.compat import Protocol


class DfCommand(Protocol):
    def df_output(self):  # type: () -> str
        raise NotImplementedError()
