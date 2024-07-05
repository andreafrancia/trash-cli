import unittest

from tests.support.mock import Mock, call

from trashcli.empty.user import User
from trashcli.lib.my_input import HardCodedInput


class TestUser(unittest.TestCase):
    def setUp(self):
        self.prepare_output_message = Mock(spec=[])
        self.input = HardCodedInput()
        self.parse_reply = Mock(spec=[])
        self.user = User(self.prepare_output_message, self.input, self.parse_reply)

    def test(self):
        self.prepare_output_message.return_value = 'output_msg'
        self.parse_reply.return_value = 'result'
        self.input.set_reply('reply')

        result = self.user.do_you_wanna_empty_trash_dirs(['trash_dirs'])

        assert [
                   result,
                   self.input.used_prompt,
                   self.prepare_output_message.mock_calls,
                   self.parse_reply.mock_calls,
               ] == [
                   'result',
                   'output_msg',
                   [call(['trash_dirs'])],
                   [call('reply')]
               ]
