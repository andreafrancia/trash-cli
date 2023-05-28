from typing import Union

from trashcli.restore.range import Range
from trashcli.restore.single import Single

Sequence = Union[Range, Single]
