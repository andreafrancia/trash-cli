import pytest

from tests.support.make_scripts import make_scripts


@pytest.mark.slow
class TestGenerateScripts:
    def test(self):
        scripts = make_scripts()

        scripts.add_script('trash', 'trashcli.put.main', 'main')
        scripts.add_script('trash-put', 'trashcli.put.main', 'main')
        scripts.add_script('trash-list', 'trashcli.list.main', 'main')
        scripts.add_script('trash-restore', 'trashcli.restore.main', 'main')
        scripts.add_script('trash-empty', 'trashcli.empty.main', 'main')
        scripts.add_script('trash-rm', 'trashcli.rm.main', 'main')

        assert scripts.created_scripts == ['trash',
                                           'trash-put',
                                           'trash-list',
                                           'trash-restore',
                                           'trash-empty',
                                           'trash-rm']
