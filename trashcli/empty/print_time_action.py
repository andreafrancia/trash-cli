# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import NamedTuple, Dict, Any

from trashcli.empty.actions import Action


class PrintTimeArgs(
    NamedTuple('PrintTimeArgs', [
        ('environ', Dict[str, str]),
        ('action', Action)
    ])):
    pass


class PrintTimeAction:
    def __init__(self, out, clock):
        self.out = out
        self.clock = clock

    def run_action(self,
                   parsed,  # type: PrintTimeArgs
                   ):
        now_value = self.clock.get_now_value(parsed.environ)
        print(now_value.replace(microsecond=0).isoformat(), file=self.out)
