# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest

import pytest

from tests.support.files import require_empty_dir
from tests.support.my_path import MyPath
from tests.test_list.cmd.support.trash_list_user import TrashListUser


@pytest.mark.slow
class Setup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.xdg_data_home = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / "topdir"
        require_empty_dir(self.top_dir)
        self.user = TrashListUser(self.xdg_data_home)

    def tearDown(self):
        self.xdg_data_home.clean_up()
        self.temp_dir.clean_up()
