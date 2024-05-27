from tests.test_put.cmd.test_put.put_fixture import PutFixture


class TestHappyPath(PutFixture):

    def test_when_file_exists(self, user, fs):
        fs.make_file("pippo", b'content')

        result = user.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        actual = {
            'file_pippo_exists': fs.exists("pippo"),
            'exit_code': result.exit_code,
            'files_in_info_dir': fs.ls_aa(
                '/home/user/.local/share/Trash/info'),
            "content_of_trashinfo": fs.read_file(
                '/home/user/.local/share/Trash/info/pippo.trashinfo'
            ),
            'files_in_files_dir': fs.ls_aa(
                '/home/user/.local/share/Trash/files'),
            "content_of_trashed_file": fs.read_file(
                '/home/user/.local/share/Trash/files/pippo'),
        }
        assert actual == {'content_of_trashed_file': b'content',
                          'content_of_trashinfo': b'[Trash Info]\n'
                                                  b'Path=/pippo\n'
                                                  b'DeletionDate=2014-01-01T00:00:00\n',
                          'exit_code': 0,
                          'file_pippo_exists': False,
                          'files_in_files_dir': ['pippo'],
                          'files_in_info_dir': ['pippo.trashinfo']}
