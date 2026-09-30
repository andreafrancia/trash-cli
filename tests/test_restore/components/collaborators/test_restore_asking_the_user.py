from tests.support.py2mock import Mock, call

from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.output_event import Quit
from trashcli.restore.output_recorder import OutputRecorder
from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.restorer import Restorer


class TestRestoreAskingTheUser:
    def setup_method(self):
        self.input = HardCodedInput()
        self.restorer = Mock(spec=Restorer)
        self.output = OutputRecorder()
        self.asking_user = RestoreAskingTheUser(self.input,
                                                self.restorer,
                                                self.output)

    def test(self):
        self.input.set_reply('0')

        self.asking_user.restore_asking_the_user(['trashed_file1',
                                                  'trashed_file2'], False)

        assert self.input.last_prompt() == 'What file to restore [0..1]: '
        assert self.restorer.mock_calls == [
            call.restore_trashed_file('trashed_file1', False)]
        assert self.output.events == []

    def test2(self):
        self.input.raise_exception(KeyboardInterrupt)

        self.asking_user.restore_asking_the_user(['trashed_file1',
                                                  'trashed_file2'], False)

        assert self.input.last_prompt() == 'What file to restore [0..1]: '
        assert self.restorer.mock_calls == []
        assert self.output.events == [Quit()]
