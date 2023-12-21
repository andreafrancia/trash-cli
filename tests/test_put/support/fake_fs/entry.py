from typing import Union

from tests.test_put.support.fake_fs.inode import INode
from tests.test_put.support.fake_fs.symlink import SymLink

Entry = Union[INode, SymLink]
