# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

import os

# Error codes (from os on *nix, hard coded for Windows):
EX_OK = getattr(os, 'EX_OK', 0)
EX_USAGE = getattr(os, 'EX_USAGE', 64)
EX_IOERR = getattr(os, 'EX_IOERR', 74)
