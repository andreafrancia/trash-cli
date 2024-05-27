from tests.test_put.cmd.test_put.put_fixture import PutFixture


class TestMultipleVolumes(PutFixture):
    def test_multiple_volumes(self, user, fs):
        fs.add_volume('/disk1')
        fs.makedirs('/disk1', 0o700)
        fs.makedirs('/disk1/.Trash-123', 0o000)
        fs.make_file("/disk1/pippo")

        result = user.run_cmd(['trash-put',
                               '-v',
                               '--home-fallback',
                               '/disk1/pippo'],
                              {'HOME': '/home/user'}, 123)

        assert result.stderr == [
            "trash-put: cannot trash regular empty file '/disk1/pippo' (from volume '/disk1')",
            'trash-put:  `- failed to trash /disk1/pippo in /home/user/.local/share/Trash, because trash dir and file to be trashed are not in the same volume, trash-dir volume: /, file volume: /disk1',
            'trash-put:  `- failed to trash /disk1/pippo in /disk1/.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /disk1/.Trash/123, parent: /disk1/.Trash',
            "trash-put:  `- failed to trash /disk1/pippo in /disk1/.Trash-123, because error during directory creation: [Errno 13] Permission denied: '/disk1/.Trash-123/files'",
            'trash-put:  `- failed to trash /disk1/pippo in /home/user/.local/share/Trash, because home fallback not enabled']
