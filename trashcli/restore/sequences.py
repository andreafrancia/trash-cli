class Sequences:
    def __init__(self, sequences):
        self.sequences = sequences

    def __repr__(self):
        return "Sequences(%s)" % repr(self.sequences)

    def all_indexes(self):
        for sequence in self.sequences:
            for index in sequence:
                yield index

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if self.sequences != other.sequences:
            return False
        return True
