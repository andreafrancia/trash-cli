import unittest
from typing import cast

import flexmock

from trashcli.fstab.volume_of import VolumeOf
from trashcli.put.fs.parent_realpath import ParentRealpath
from trashcli.put.fs.volume_of_parent import VolumeOfParent


class TestVolumeOfParent(unittest.TestCase):
    def setUp(self):
        self.volumes = flexmock.Mock(spec=VolumeOf)
        self.parent_realpath = flexmock.Mock(spec=ParentRealpath)
        self.volume_of_parent = VolumeOfParent(cast(VolumeOf, self.volumes),
                                               cast(ParentRealpath,
                                                    self.parent_realpath))
    def test(self):
        self.parent_realpath.should_receive('parent_realpath').\
            with_args('/path/to/file').\
            and_return('parent-realpath')
        self.volumes.should_receive('volume_of').with_args("parent-realpath").\
            and_return('volume-of-parent')

        result = self.volume_of_parent.volume_of_parent('/path/to/file')

        assert result == 'volume-of-parent'
