import os
import unittest

import pytest
from scripts.make_scripts import make_scripts
from trashcli import base_dir


def script_path_without_base_dir_for(name):
    return os.path.join(name)


def script_path_for(name):
    return os.path.join(base_dir, script_path_without_base_dir_for(name))


@pytest.mark.slow
class TestGenerateScripts(unittest.TestCase):
    def test(self):
        scripts = make_scripts()

        scripts.add_script('trash', 'trashcli.put.main', 'main')
        scripts.add_script('trash-put', 'trashcli.put.main', 'main')
        scripts.add_script('trash-list', 'trashcli.list.main', 'main')
        scripts.add_script('trash-restore', 'trashcli.restore.main', 'main')
        scripts.add_script('trash-empty', 'trashcli.empty.main', 'main')
        scripts.add_script('trash-rm', 'trashcli.rm.main', 'main')

        self.assertEqual(['trash',
                          'trash-put',
                          'trash-list',
                          'trash-restore',
                          'trash-empty',
                          'trash-rm'],
                         scripts.created_scripts)
