from abc import ABCMeta, abstractmethod

import six

from trashcli.restore.output_event import OutputEvent


@six.add_metaclass(ABCMeta)
class Output:
    @abstractmethod
    def quit(self):
        raise NotImplementedError

    @abstractmethod
    def die(self, msg):
        raise NotImplementedError

    @abstractmethod
    def println(self, msg):
        raise NotImplementedError

    @abstractmethod
    def append_event(self,
                     event,  # type: OutputEvent
                     ):
        raise NotImplementedError
