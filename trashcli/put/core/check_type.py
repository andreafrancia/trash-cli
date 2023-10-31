from enum import Enum


class CheckType(Enum):
    NoCheck = 'NoCheck'
    TopTrashDirCheck = 'TopTrashDirCheck'


NoCheck = CheckType.NoCheck
TopTrashDirCheck = CheckType.TopTrashDirCheck
