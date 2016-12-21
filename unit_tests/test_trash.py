# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

from __future__ import absolute_import

from trashcli.restore import TrashedFile
from integration_tests.files import write_file, require_empty_dir

import os
from unittest import TestCase

class TestTrashedFile(TestCase) :

    def test_restore_create_needed_directories(self):
        require_empty_dir('sandbox')

        write_file('sandbox/TrashDir/files/bar')
        instance = TrashedFile('sandbox/foo/bar',
                               'deletion_date', 'info_file',
                               'sandbox/TrashDir/files/bar', 'trash_dirctory')
        instance.restore()
        assert os.path.exists("sandbox/foo/bar")

