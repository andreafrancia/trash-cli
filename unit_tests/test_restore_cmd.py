from trashcli.trash import RestoreCmd
from nose.tools import assert_equal

# Try Python 2 import; if ImportError occurs, use Python 3 import
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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

        assert_equal('trash-restore 1.2.3\n', stdout.getvalue())

