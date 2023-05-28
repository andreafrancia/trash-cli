from typing import List

from trashcli.restore.output import Output
from trashcli.restore.output_event import Quit, Die, Println, OutputEvent


class OutputRecorder(Output):
    def __init__(self):  # type: (...) -> None
        self.events = []  # type: List[OutputEvent]

    def quit(self):  # type: () -> None
        self.append_event(Quit())

    def die(self, msg):  # type: (str) -> None
        self.append_event(Die(msg))

    def println(self, msg):  # type: (str) -> None
        self.append_event(Println(msg))

    def append_event(self,
                     event,  # type: OutputEvent
                     ):  # type: (...) -> None
        self.events.append(event)

    def apply_to(self, output,  # type: Output
                 ):   # type: (...) -> None
        for event in self.events:
            output.append_event(event)
