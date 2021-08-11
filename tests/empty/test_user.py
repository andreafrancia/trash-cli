import unittest

from trashcli.empty import User
from mock import Mock, call


class TestUser(unittest.TestCase):
    def setUp(self):
        self.prepare_output_message = Mock(spec=[])
        self.input = Mock(spec=[])
        self.parse_reply = Mock(spec=[])
        self.user = User(self.prepare_output_message, self.input, self.parse_reply)

    def test(self):
        self.prepare_output_message.return_value = 'output_msg'
        self.parse_reply.return_value = 'result'
        self.input.return_value = 'reply'

        result = self.user.do_you_wanna_empty_trash_dirs(['trash_dirs'])

        assert [
                   result,
                   self.input.mock_calls,
                   self.prepare_output_message.mock_calls,
                   self.parse_reply.mock_calls,
               ] == [
                   'result',
                   [call('output_msg')],
                   [call(['trash_dirs'])],
                   [call('reply')]
               ]
