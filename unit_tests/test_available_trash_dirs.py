# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import AvailableTrashDirs
from nose.tools import istest, assert_in, assert_not_in

@istest
class Describe_AvailableInfoDirs_on_volume_trashcans:
    @istest
    def the_method_2_is_always_in(self):
        self.having_uid(123)
        self.having_volumes('/usb')
        
        assert_in('/usb/.Trash-123', self.trashdirs())

    @istest
    def the_method_1_is_in_if_it_is_a_sticky_dir(self):
        self.having_uid(123)
        self.having_volumes('/usb')
        self.having_sticky_Trash_dir()

        assert_in('/usb/.Trash/123', self.trashdirs())

    @istest
    def the_method_1_is_not_considered_if_not_sticky_dir(self):
        self.having_uid(123)
        self.having_volumes('/usb')
        self.having_non_sticky_Trash_dir()

        assert_not_in('/usb/.Trash/123', self.trashdirs())

    @istest
    def should_return_home_trashcan_when_XDG_DATA_HOME_is_defined(self):
        self.having_XDG_DATA_HOME('~/.local/share')

        assert_in('~/.local/share/Trash', self.trashdirs())

    def trashdirs(self):
        result = collector()
        AvailableTrashDirs(
            environ=self.environ, 
            getuid=lambda:self.uid, 
            list_volumes=lambda:self.volumes,
            is_sticky_dir=lambda path: self.Trash_dir_is_sticky
        ).for_each_trashdir_and_volume(result)
        return result.trash_dirs

    def setUp(self):
        self.uid = -1
        self.volumes = ()
        self.Trash_dir_is_sticky = not_important_for_now()
        self.environ = {}
    def having_uid(self, uid): self.uid = uid
    def having_volumes(self, *volumes): self.volumes = volumes
    def having_sticky_Trash_dir(self): self.Trash_dir_is_sticky = True
    def having_non_sticky_Trash_dir(self): self.Trash_dir_is_sticky = False
    def having_XDG_DATA_HOME(self, XDG_DATA_HOME):
        self.environ['XDG_DATA_HOME'] = XDG_DATA_HOME

@istest
def test():
    result = collector()
    AvailableTrashDirs(
        environ       = dict(XDG_DATA_HOME='~/.local/share'),
        getuid        = lambda: 0,
        list_volumes  = lambda: [],
        is_sticky_dir = lambda path: False
    ).for_home_trashcan_info_dir_path(result)

    assert result.trash_dirs == ['~/.local/share/Trash']

def not_important_for_now(): None

class collector:
    def __init__(self):
        self.trash_dirs = []
    def __call__(self, trash_dir, volume):
        self.trash_dirs.append(trash_dir)
        

