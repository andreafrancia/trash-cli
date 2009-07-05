# trash-admin list volume sub command tests

from unittest import TestCase
from nose.tools import *
from trashcli.cli.admin import AdminCommand
from trashcli.logger import *
from trashcli.filesystem import *

class AdminListVolumeTest(TestCase):
    def test_list_volumes(self):
        class FakeFileSystem(object):
            def volumes(self):
                yield Path("/")
                yield Path("/mnt")
                yield Path("/media/disk")

        class FakeTrashSystem(object):
            def trash_directories(self):
                return []

        logger = MemoryLogger()
        filesystem = FakeFileSystem()

        instance = AdminCommand(logger, filesystem, FakeTrashSystem())
        instance.execute("list-volumes")

        assert_equals(
            logger.messages,
            [("reply", "/"),
             ("reply", "/mnt"),
             ("reply", "/media/disk")])


