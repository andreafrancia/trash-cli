from tests.support.py2mock import Mock

from tests.support.make_scripts import Scripts
from tests.support.make_scripts import script_path_without_base_dir_for


class TestListOfCreatedScripts:
    def setup_method(self):
        self.bindir = Scripts(make_file_executable=Mock(), write_file=Mock())

    def test_is_empty_on_start_up(self):
        assert self.bindir.created_scripts == []

    def test_collect_added_script(self):
        self.bindir.add_script('foo-command', 'foo-module', 'main')
        assert self.bindir.created_scripts == [
            script_path_without_base_dir_for('foo-command')]
