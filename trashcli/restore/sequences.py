from typing import NamedTuple, List

from trashcli.restore.index import Sequence


class Sequences(NamedTuple('Sequences', [
    ('sequences', List[Sequence]),
])):
    def all_indexes(self):
        for sequence in self.sequences:
            for index in sequence:
                yield index
