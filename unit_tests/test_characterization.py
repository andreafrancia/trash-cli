# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import istest

from trashcli.trash import GlobalTrashCan

@istest
class GlobalTrashCanTest:

    def test_home_dir_path(self):
        a=GlobalTrashCan(environ = {'XDG_DATA_HOME': './XDG_DATA_HOME'})
        home_trash = a._home_trash_dir_path()

        assert './XDG_DATA_HOME/Trash' == home_trash

