# Copyright (C) 2008-2012 Andrea Francia Trivolzio(PV) Italy

import os

from nose.tools import assert_equals, assert_true

from integration_tests.files import require_empty_dir
from trashcli.put import TrashDirectoryForPut, RealFs
from mock import Mock

join = os.path.join

class TestTrashDirectory_persit_trash_info:
    def setUp(self):
        self.trashdirectory_base_dir = os.path.realpath(
                "./sandbox/testTrashDirectory")
        require_empty_dir(self.trashdirectory_base_dir)

        self.instance = TrashDirectoryForPut(
                self.trashdirectory_base_dir,
                "/",
                RealFs())
        self.logger = Mock()

    def persist_trash_info(self, basename, content):
        return self.instance.persist_trash_info(basename,
                                                content,
                                                self.logger)

    def test_persist_trash_info_first_time(self):

        trash_info_file = self.persist_trash_info('dummy-path', b'content')
        assert_equals(join(self.trashdirectory_base_dir,'info', 'dummy-path.trashinfo'), trash_info_file)

        assert_equals('content', read(trash_info_file))

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        for i in range(1,100) :
            content=b'trashinfo content'
            trash_info_file = self.persist_trash_info('dummy-path', content)

            assert_equals("dummy-path_%s.trashinfo" % i,
                    os.path.basename(trash_info_file))
            assert_equals('trashinfo content', read(trash_info_file))

    def test_persist_trash_info_other_times(self):
        self.test_persist_trash_info_first_100_times()

        for i in range(101,200) :
            trash_info_file = self.persist_trash_info('dummy-path',b'content')
            trash_info_id = os.path.basename(trash_info_file)
            assert_true(trash_info_id.startswith("dummy-path_"))
            assert_equals('content', read(trash_info_file))
    test_persist_trash_info_first_100_times.stress_test = True
    test_persist_trash_info_other_times.stress_test = True

def read(path):
    return open(path).read()

