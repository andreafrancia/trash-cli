from trashcli.restore.run_restore_action import original_location_matches_path


class TestOriginalLocationMatchesPath:
    def test1(self):
        assert original_location_matches_path("/full/path", "/full")

    def test2(self):
        assert original_location_matches_path("/full/path", "/full/path")

    def test3(self):
        assert not original_location_matches_path("/prefix-extension", "/prefix")

    def test_root(self):
        assert original_location_matches_path("/any/path", "/")
