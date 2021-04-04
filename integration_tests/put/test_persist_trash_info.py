# Copyright (C) 2008-2012 Andrea Francia Trivolzio(PV) Italy

import os
import unittest

from trashcli.fs import read_file
from unit_tests.support import MyPath
from trashcli.put import RealFs, persist_trash_info
from mock import Mock

join = os.path.join


class Test_persist_trash_info(unittest.TestCase):
    def setUp(self):
        self.info_dir = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.logger = Mock()

    def persist_trash_info(self, basename, content):
        return persist_trash_info(self.info_dir, self.fs, basename, content,
                                  self.logger)

    def test_persist_trash_info_first_time(self):
        trash_info_file = self.persist_trash_info('dummy-path', b'content')

        assert self.info_dir / 'dummy-path.trashinfo' == trash_info_file
        assert 'content' == read_file(trash_info_file)

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        for i in range(1,100) :
            trash_info_file = self.persist_trash_info('dummy-path', b'content')

            assert ("dummy-path_%s.trashinfo" % i ==
                    os.path.basename(trash_info_file))
            assert 'content' == read_file(trash_info_file)

    def test_persist_trash_info_other_times(self):
        self.test_persist_trash_info_first_100_times()

        for i in range(101,200) :
            trash_info_file = self.persist_trash_info('dummy-path',b'content')
            trash_info_id = os.path.basename(trash_info_file)
            assert trash_info_id.startswith("dummy-path_")
            assert 'content' == read_file(trash_info_file)
    test_persist_trash_info_first_100_times.stress_test = True
    test_persist_trash_info_other_times.stress_test = True


