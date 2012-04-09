from trashcli.trash import ListCmd
from StringIO import StringIO

class TestListCmd:
    def test_something(self):
        out=StringIO()
        err=StringIO()
        trash_list=ListCmd(out, err, {})

        trash_list.list_trash()

