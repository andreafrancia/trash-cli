from tests.test_list.cmd.support.trash_list_user import adjust_for_root


class TestAdjustForRoot:
    def test(self):
        assert adjust_for_root("disk") == "disk"
        assert adjust_for_root("/disk") == "disk"
        assert adjust_for_root("//disk") == "disk"
