from typing import NamedTuple


class Sequences(NamedTuple('Sequences', [
    ('sequences', list),
])):
    def all_indexes(self):
        for sequence in self.sequences:
            for index in sequence:
                yield index
