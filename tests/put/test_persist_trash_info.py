# Copyright (C) 2008-2021 Andrea Francia Trivolzio(PV) Italy

import unittest

import pytest

from trashcli.fs import read_file
from ..support import MyPath
from trashcli.put.real_fs import RealFs
from trashcli.put.info_dir import InfoDir
from mock import Mock


@pytest.mark.slow
class Test_persist_trash_info(unittest.TestCase):
    def setUp(self):
        self.path = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.logger = Mock()
        self.suffix = Mock()
        self.suffix.suffix_for_index.side_effect = lambda i: '.suffix-%s' % i
        self.info_dir = InfoDir(self.fs,
                                self.logger,
                                self.suffix)

    def test_persist_trash_info_first_time(self):
        trash_info_file = self.info_dir.persist_trash_info(
            'dummy-path', b'content', 'trash-put', 99, self.path)

        assert self.path / 'dummy-path.suffix-0.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        trash_info_file = self.info_dir.persist_trash_info(
            'dummy-path', b'content', 'trash-put', 99, self.path)

        assert self.path / 'dummy-path.suffix-1.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def tearDown(self):
        self.path.clean_up()
