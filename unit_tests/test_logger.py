from unittest import TestCase
from nose.tools import *

from trashcli.logger import *

class MemoryLoggerTest(TestCase):
    def test_message_are_retrievables(self):
        logger = MemoryLogger()
        logger.info("1")
        logger.error("2")
        logger.error("3")
        logger.warning("4")
        logger.fatal("5")

        assert_equals(5, len(logger.messages))

        assert_equals(("info", "1"), logger.messages[0])
        assert_equals(("error", "2"), logger.messages[1])
        assert_equals(("error", "3"), logger.messages[2])
        assert_equals(("warning", "4"), logger.messages[3])
        assert_equals(("fatal", "5"), logger.messages[4])

