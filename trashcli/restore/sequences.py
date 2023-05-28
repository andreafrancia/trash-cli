from typing import NamedTuple

from trashcli.restore.index import Sequence


class Sequences(NamedTuple('Sequences', [
    ('sequences', list[Sequence]),
])):
    def all_indexes(self):
        for sequence in self.sequences:
            for index in sequence:
                yield index
