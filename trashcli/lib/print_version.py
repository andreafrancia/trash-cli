# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy

from __future__ import absolute_import
from __future__ import print_function

import os

import six
from typing import NamedTuple


class PrintVersionArgs(
    NamedTuple('PrintVersionArgs', [
        ('argv0', str),
    ])):

    def program_name(self):
        return os.path.basename(self.argv0)


class PrintVersionAction:
    def __init__(self, out, version):
        self.out = out
        self.version = version

    def run_action(self,
                   args,  # type: PrintVersionArgs
                   ):
        print_version(self.out, args.program_name(), self.version)


def print_version(out, program_name, version):
    print("%s %s" % (program_name, six.text_type(version)), file=out)
