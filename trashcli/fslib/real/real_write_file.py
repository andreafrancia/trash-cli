from trashcli.fslib.protocols.write_file import WriteFile


class RealWriteFile(WriteFile):
    def write_file(self, name, contents):
        with open(name, 'w') as f:
            f.write(contents)
