import flexmock

from tests.test_put.cmd.test_put.put_fixture import PutFixture
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.exit_codes import EX_OK
from trashcli.put.core.logs import LogTag


class TestPut(PutFixture):

    def test_when_moving_file_in_trash_dir_fails(self, user, fs):
        fs.touch("foo")
        fs.fail_move_on("/foo")

        result = user.run_cmd(['trash-put', '-v', '/foo'])

        assert result.exit_code_and_stderr() == [EX_IOERR, [
            "trash-put: cannot trash regular empty file '/foo' (from volume '/')",
            'trash-put:  `- failed to trash /foo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
            'trash-put:  `- failed to trash /foo in /.Trash-123, because failed to move /foo in /.Trash-123/files: move failed']]

    def test_when_file_does_not_exist(self, user, fs):
        result = user.run_cmd(['trash-put', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash non existent 'non-existent'"]]

    def test_when_file_does_not_exist_with_force(self, user):
        result = user.run_cmd(['trash-put', '-f', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result.exit_code_and_stderr() == [EX_OK, []]

    def test_put_does_not_try_to_trash_non_existing_file(self, user):
        result = user.run_cmd(['trash-put', '-vvv', 'non-existing'],
                              {"HOME": "/home/user"}, 123)

        assert result.exit_code_and_stderr() == \
               [
                   EX_IOERR,
                   ["trash-put: cannot trash non existent 'non-existing'"]
               ]

    def test_when_file_cannot_be_trashed(self, user, fs):
        fs.touch("foo")
        fs.fail_move_on("foo")

        result = user.run_cmd(['trash-put', 'foo'])

        assert (result.exit_code_and_logs(LogTag.trash_failed) ==
                (74, [
                    "cannot trash regular empty file 'foo' (from volume '/')",
                    ' `- failed to trash foo in /.Trash/123, because trash dir '
                    'cannot be created because its parent does not exists, '
                    'trash-dir: /.Trash/123, parent: /.Trash',
                    ' `- failed to trash foo in /.Trash-123, because failed to '
                    'move foo in /.Trash-123/files: move failed',
                ]))

    def test_when_there_is_no_working_trash_dir(self, user, fs):
        fs.make_file("pippo")
        fs.makedirs('/.Trash-123', 0o000)

        result = user.run_cmd(['trash-put', '-v', 'pippo'], {}, 123)

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            [
                "trash-put: cannot trash regular empty file 'pippo' (from volume '/')",
                'trash-put:  `- failed to trash pippo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
                "trash-put:  `- failed to trash pippo in /.Trash-123, because error during directory creation: [Errno 13] Permission denied: '/.Trash-123/files'"
            ]
        ]
    def test_when_a_error_during_move(self, user, fs):
        fs.make_file("pippo", b'content')

        result = user.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        assert False == fs.exists("pippo")
        assert EX_OK == result.exit_code
        assert ['pippo.trashinfo'] == fs.ls_aa(
            '/home/user/.local/share/Trash/info')
        trash_info = fs.read_file(
            '/home/user/.local/share/Trash/info/pippo.trashinfo'
        ).decode('utf-8')
        assert trash_info == '[Trash Info]\nPath=/pippo\nDeletionDate=2014-01-01T00:00:00\n'
        assert ['pippo'] == fs.ls_aa('/home/user/.local/share/Trash/files')
        assert fs.read_file('/home/user/.local/share/Trash/files/pippo') == b'content'


    def test_when_file_move_fails(self, user, fs):
        flexmock.flexmock(fs).should_receive('move'). \
            and_raise(IOError, 'No space left on device')
        fs.make_file("pippo", b'content')

        result = user.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        actual = {
            'file_pippo_exists': fs.exists("pippo"),
            'exit_code': result.exit_code,
            'stderr': result.stderr,
            'files_in_info_dir': fs.ls_aa(
                '/home/user/.local/share/Trash/info'),
            "content_of_trashinfo": fs.read_null(
                '/home/user/.local/share/Trash/info/pippo.trashinfo'),
            'files_in_files_dir': fs.ls_aa(
                '/home/user/.local/share/Trash/files'),
            "content_of_trashed_file": fs.read_null(
                '/home/user/.local/share/Trash/files/pippo'),
        }
        assert actual == {'content_of_trashed_file': None,
                          'content_of_trashinfo': None,
                          'exit_code': EX_IOERR,
                          'stderr': [
                              "trash-put: cannot trash regular file 'pippo' (from volume '/')",
                              'trash-put:  `- failed to trash pippo in /home/user/.local/share/Trash, because failed to move pippo in /home/user/.local/share/Trash/files: No space left on device',
                              'trash-put:  `- failed to trash pippo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
                              'trash-put:  `- failed to trash pippo in /.Trash-123, because failed to move pippo in /.Trash-123/files: No space left on device'],
                          'file_pippo_exists': True,
                          'files_in_files_dir': [],
                          'files_in_info_dir': []}

    def test_when_it_fails_to_prepare_trash_info_data(self, user, fs):
        flexmock.flexmock(fs).should_receive('parent_realpath2'). \
            and_raise(IOError, 'Corruption')
        fs.make_file("foo")

        result = user.run_cmd(['trash-put', '-v', 'foo'],
                              {"HOME": "/home/user"}, 123)
        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            [
                "trash-put: cannot trash regular empty file 'foo' (from volume '/')",
                'trash-put:  `- failed to trash foo in /home/user/.local/share/Trash, because failed to generate trashinfo content: Corruption',
                'trash-put:  `- failed to trash foo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
                'trash-put:  `- failed to trash foo in /.Trash-123, because failed to generate trashinfo content: Corruption']]
