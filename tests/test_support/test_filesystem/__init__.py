
import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real_fs_operations import RealHasStickyBit, RealMkDirs, \
    RealWriteFile, RealIsStickyDir

