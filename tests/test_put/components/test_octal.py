from trashcli.put.octal import octal

class TestOctal:
    def test(self):
        assert octal(16877) == '0o40755'
