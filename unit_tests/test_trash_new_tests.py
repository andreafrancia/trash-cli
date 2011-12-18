# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import (assert_true, assert_equals)
from unittest import TestCase
from trashcli.trash import GlobalTrashCan

class TestGlobalTrashCan(TestCase):
    def test_the_attempt_of_deleting_a_dot_directory_should_signaled_as_error(self):

	argument="."

	class StubReporter:
	    def __init__(self):
		self.has_been_called=False

	    def unable_to_trash_dot_entries(self,file):
		self.has_been_called=True
		assert_equals(file, argument)

	reporter=StubReporter()
	trashcan = GlobalTrashCan(reporter=reporter)

	trashcan.trash('.')
	assert_true(reporter.has_been_called)

