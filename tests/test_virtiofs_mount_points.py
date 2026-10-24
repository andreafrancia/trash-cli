import sys
import unittest
from collections import namedtuple
from unittest.mock import Mock, patch

from trashcli.fstab.real.os_mount_points import os_mount_points


class TestVirtiofsMountPoints(unittest.TestCase):
    def test_virtual_filesystem_discovery(self):
        partition = namedtuple('Partition', 'device mountpoint fstype')
        physical = partition('/dev/fictional', '/fixture-root', 'ext4')
        shared = partition('fictional-share', '/fixture-shared', 'virtiofs')
        pseudo = partition('proc', '/fixture-proc', 'proc')
        missing = partition('missing-share', '/fixture-missing', 'virtiofs')
        psutil = Mock()
        psutil.disk_partitions.side_effect = lambda all=False: (
            [physical, shared, pseudo, missing] if all else [physical])
        with patch.dict(sys.modules, {'psutil': psutil}), patch(
                'trashcli.fstab.real.os_mount_points.os.path.isdir',
                side_effect=lambda path: path != '/fixture-missing'):
            result = list(os_mount_points())
        self.assertEqual(result, ['/fixture-root', '/fixture-shared'])
