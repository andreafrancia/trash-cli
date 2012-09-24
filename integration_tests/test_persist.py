# Copyright (C) 2008-2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import TrashDirectory
from trashcli.trash import TrashInfo
from integration_tests.files import require_empty_dir

from nose.tools import assert_equals, assert_true

import os
from datetime import datetime
from textwrap import dedent
join = os.path.join

class TestTrashDirectory_persit_trash_info:
    def setUp(self):
        self.trashdirectory_base_dir = os.path.realpath("./sandbox/testTrashDirectory")
        require_empty_dir(self.trashdirectory_base_dir)

        self.instance=TrashDirectory(self.trashdirectory_base_dir, "/")

    def persist_trash_info(self, basename, content):
        return self.instance.persist_trash_info(
                self.instance.info_dir, basename,content)

    def test_persist_trash_info_first_time(self):
        trash_info=TrashInfo("dummy-path", datetime(2007,01,01))

        basename=os.path.basename(trash_info.path)
        content=trash_info.render()
        trash_info_file = self.persist_trash_info(basename, content)
        assert_equals(join(self.trashdirectory_base_dir,'info', 'dummy-path.trashinfo'), trash_info_file)

        assert_equals(dedent("""\
                      [Trash Info]
                      Path=dummy-path
                      DeletionDate=2007-01-01T00:00:00
                      """), read(trash_info_file))

    def test_persist_trash_info_first_100_times(self):
        self.test_persist_trash_info_first_time()

        for i in range(1,100) :
            trash_info=TrashInfo("dummy-path", datetime(2007,01,01))

            basename=os.path.basename(trash_info.path)
            content=trash_info.render()
            trash_info_file = self.persist_trash_info(basename, content)

            assert_equals("dummy-path_%s.trashinfo" % i, os.path.basename(trash_info_file))
            assert_equals(dedent("""\
                [Trash Info]
                Path=dummy-path
                DeletionDate=2007-01-01T00:00:00
                """), read(trash_info_file))

    def test_persist_trash_info_other_times(self):
        self.test_persist_trash_info_first_100_times()

        for i in range(101,200) :
            trash_info=TrashInfo("dummy-path", datetime(2007,01,01))

            basename=os.path.basename(trash_info.path)
            content=trash_info.render()
            trash_info_file = self.persist_trash_info(basename,content)
            trash_info_id = os.path.basename(trash_info_file)
            assert_true(trash_info_id.startswith("dummy-path_"))
            assert_equals(dedent("""\
                [Trash Info]
                Path=dummy-path
                DeletionDate=2007-01-01T00:00:00
                """), read(trash_info_file))
    test_persist_trash_info_first_100_times.stress_test = True
    test_persist_trash_info_other_times.stress_test = True

def read(path):
    return file(path).read()

