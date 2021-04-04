# Copyright (C) 2008-2012 Andrea Francia Trivolzio(PV) Italy

import os
import unittest

from trashcli.fs import read_file
from unit_tests.support import MyPath
from trashcli.put import RealFs, PersistTrashInfo
from mock import Mock

join = os.path.join


class Test_persist_trash_info(unittest.TestCase):
    def setUp(self):
        self.info_dir = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.logger = Mock()
        self.suffix = Mock()
        self.suffix.suffix_for_index.side_effect = lambda i: '.suffix-%s' % i
        self.persist_trash_info = PersistTrashInfo(self.info_dir,
                                                   self.fs,
                                                   self.logger,
                                                   self.suffix)

    def test_persist_trash_info_first_time(self):
        trash_info_file = self.persist_trash_info.persist_trash_info(
            'dummy-path', b'content')

        assert self.info_dir / 'dummy-path.suffix-0.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        trash_info_file = self.persist_trash_info.persist_trash_info(
            'dummy-path', b'content')

        assert self.info_dir / 'dummy-path.suffix-1.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def tearDown(self):
        self.info_dir.clean_up()
