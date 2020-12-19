from trashcli.trash import TrashDirs
from mock import Mock, call
from unit_tests.tools import assert_equal

class TestListTrashinfo:
    def test_howto_list_trashdirs(self):
        out = Mock()
        environ = {'HOME':'/home/user'}
        trashdirs = TrashDirs(
                environ = environ,
                getuid = lambda:123,
                list_volumes = lambda:['/vol', '/vol2'],
                top_trashdir_rules = Mock(),
                )
        trashdirs.on_trash_dir_found = out
        trashdirs.list_trashdirs()

        assert_equal([call('/home/user/.local/share/Trash', '/'),
                      call('/vol/.Trash-123', '/vol'),
                      call('/vol2/.Trash-123', '/vol2')],
                     out.mock_calls)
