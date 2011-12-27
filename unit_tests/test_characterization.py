# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals, istest
import unittest

from trashcli.trash import GlobalTrashCan

class GlobalTrashCanTest(unittest.TestCase):
    def test_something(self):
        assert_equals(1,1)

    def test_fixture(self):
        def do_nothing(info_path, path): pass
        a=GlobalTrashCan()
        a.for_all_trashed_file(do_nothing)

    def test_home_dir_path(self):
        a=GlobalTrashCan(environ = {'XDG_DATA_HOME': './XDG_DATA_HOME'})
        home_trash = a._home_trash_dir_path()

        assert './XDG_DATA_HOME/Trash' == home_trash
        
from trashcli.trash import TrashInfo
from datetime import datetime
@istest
class describe_parsing:
    def test_parse(self):
        trashinfo=(
        "[TrashInfo]\n"
        "Path=/foo\n"
        "DeletionDate=2000-01-01T00:00:01\n")
        result = TrashInfo.parse(trashinfo)
        self.assertEqual(result.path, "home/andrea/prova.txt")
        self.assert_(isinstance(result.deletion_date,datetime))
        self.assertEqual(result.deletion_date,
                         datetime(2007, 7, 23, 23, 45, 07))

