# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from tests.support.asserts import assert_equals_with_unidiff
from tests.support.my_path import MyPath
from tests.test_list.cmd.support.trash_list_user import TrashListUser


class TestAlternateTrashDir:
    def setup_method(self):
        self.user = TrashListUser(MyPath.make_temp_dir())
        self.top_dir = MyPath.make_temp_dir()

    def test_should_list_contents_of_alternate_trashdir(self):
        self.user.set_fake_uid(123)
        self.user.add_volume(self.top_dir)
        self.user.top2(self.top_dir).add_trashinfo4('file', "2000-01-01")

        output = self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:00 %s/file\n" %
                                   self.top_dir, output.stdout)
