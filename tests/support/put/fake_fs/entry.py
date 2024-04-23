from typing import Union

from tests.support.put.fake_fs.inode import INode
from tests.support.put.fake_fs.symlink import SymLink

Entry = Union[INode, SymLink]
