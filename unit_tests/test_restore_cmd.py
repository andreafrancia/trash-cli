from trashcli.restore import RestoreCmd
from nose.tools import assert_equals
from StringIO import StringIO

class TestTrashRestoreCmd:
    def test_should_print_version(self):
        stdout = StringIO()
        cmd = RestoreCmd(stdout=stdout,
                         stderr=None,
                         environ=None,
                         exit = None,
                         input=None,
                         version = '1.2.3')

        cmd.run(['trash-restore', '--version'])

        assert_equals('trash-restore 1.2.3\n', stdout.getvalue())

