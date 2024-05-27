from trashcli.fs import FileReader


class FakeFileReader(FileReader):
    def __init__(self, contents=None):
        self.contents = contents

    def set_content(self, contents):
        self.contents = contents

    def read_file(self, path):
        return self.contents