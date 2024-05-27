
from tests.support.make_scripts import Scripts
from tests.test_dev_tools.support.null_script_fs import NullScriptFs
from trashcli.path import Path


class TestListOfCreatedScripts:
    def setup_method(self):
        fake_fs = NullScriptFs()
        self.scripts = Scripts(fake_fs, Path("root"))

    def test_is_empty_on_start_up(self):
        assert self.scripts.created_scripts == []

    def test_collect_added_script(self):
        self.scripts.add_script('foo-command', 'foo-module', 'main')
        assert self.scripts.created_scripts == ["foo-command"]
