
import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real_fs_operations import RealMkDirs, \
    RealWriteFile
from trashcli.fslib.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real_has_sticky_bit import RealHasStickyBit

