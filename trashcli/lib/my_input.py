from abc import abstractmethod, ABCMeta

import six
from six.moves import input as _my_input


@six.add_metaclass(ABCMeta)
class Input:
    @abstractmethod
    def read_input(self, prompt):  # type: (str) -> str
        raise NotImplementedError


class RealInput(Input):
    def read_input(self, prompt):  # type: (str) -> str
        return _my_input(prompt)


class HardCodedInput(Input):
    def __init__(self, reply=None):
        self.reply, self.exception = self._reply(reply)

    def set_reply(self, reply):
        self.reply, self.exception = self._reply(reply)

    def _reply(self, reply):
        if reply is None:
            return None, ValueError("No reply set")
        else:
            return reply, None
    def raise_exception(self, exception):
        self.exception = exception

    def read_input(self, prompt):  # type: (str) -> str
        self.used_prompt = prompt
        if self.exception:
            raise self.exception
        return self.reply

    def last_prompt(self):
        return self.used_prompt
