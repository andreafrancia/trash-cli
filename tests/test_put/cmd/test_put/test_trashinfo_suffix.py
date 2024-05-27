from tests.test_put.cmd.test_put.put_fixture import PutFixture


class TestTrashInfoSuffix(PutFixture):

    def test_when_needs_a_different_suffix(self, user, fs):
        fs.touch("/foo")
        fs.fail_atomic_create_unless("foo_1.trashinfo")

        user.run_cmd(['trash-put', '/foo'])

        assert fs.ls_aa('/.Trash-123/files') == ['foo_1']

    def test_when_needs_a_random_suffix(self, user, fs):
        fs.touch("/foo")
        fs.fail_atomic_create_unless("foo_123.trashinfo")
        user.add_random_int(123)

        user.run_cmd(['trash-put', '/foo'])

        assert fs.ls_aa('/.Trash-123/files') == ['foo_123']

    def test_when_a_trashinfo_file_already_exists(self, user, fs):
        user.touch_and_trash("/foo")
        user.touch_and_trash("/foo")
        user.touch_and_trash("/foo")

        assert fs.ls_aa('/.Trash-123/info') == [
            'foo.trashinfo',
            'foo_1.trashinfo',
            'foo_2.trashinfo'
        ]
