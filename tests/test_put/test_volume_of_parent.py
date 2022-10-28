import unittest

import flexmock
from typing import cast

from tests.support.volumes_mock import volumes_mock
from trashcli.fstab import Volumes
from trashcli.put.parent_realpath import ParentRealpath
from trashcli.put.volume_of_parent import VolumeOfParent


class TestVolumeOfParent(unittest.TestCase):
    def setUp(self):
        self.volumes = flexmock.Mock(spec=Volumes)
        self.parent_realpath = flexmock.Mock(spec=ParentRealpath)
        self.volume_of_parent = VolumeOfParent(cast(Volumes, self.volumes),
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
