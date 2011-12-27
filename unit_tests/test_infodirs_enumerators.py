# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import AvailableTrashDir
from nose.tools import istest, assert_in, assert_not_in

@istest
class Describe_AvailableInfoDirs:
    @istest
    def the_method_2_is_always_in(self):
        dirs=AvailableTrashDir(environ={}, 
                               getuid=lambda:123, 
                               list_volumes=lambda:['/usb'])

        result = collector()
        dirs.for_each_volume_trashcans(result)

        assert_in('/usb/.Trash-123', result.calls)

    @istest
    def the_method_1_is_in_if_it_is_a_sticky_dir(self):
        dirs=AvailableTrashDir(environ={}, 
                               getuid=lambda:123, 
                               list_volumes=lambda:['/usb'],
                               is_sticky_dir=lambda path: True)

        result = collector()
        dirs.for_each_volume_trashcans(result)

        assert_in('/usb/.Trash/123', result.calls)

    @istest
    def the_method_1_is_not_considered_if_not_sticky_dir(self):
        dirs=AvailableTrashDir(environ={}, 
                               getuid=lambda:123, 
                               list_volumes=lambda:['/usb'],
                               is_sticky_dir=lambda path: False)

        result = collector()
        dirs.for_each_volume_trashcans(result)

        assert_not_in('/usb/.Trash/123', result.calls)

class collector:
    def __init__(self):
        self.calls = []
    def __call__(self, trash_dir, volume):
        self.calls.append(trash_dir)
        

