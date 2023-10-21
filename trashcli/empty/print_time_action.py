# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from __future__ import print_function

from typing import NamedTuple

from trashcli.lib.environ import Environ


class PrintTimeArgs(
    NamedTuple('PrintTimeArgs', [
        ('environ', Environ),
    ])):
    pass


class PrintTimeAction:
    def __init__(self, out, clock):
        self.out = out
        self.clock = clock

    def run_action(self,
                   args,  # type: PrintTimeArgs
                   ):
        now_value = self.clock.get_now_value(args.environ)
        print(now_value.replace(microsecond=0).isoformat(), file=self.out)
