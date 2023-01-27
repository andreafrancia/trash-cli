class Single:
    def __init__(self, index):
        self.index = index

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if self.index != other.index:
            return False
        return True

    def __iter__(self):
        return iter([self.index])

    def __repr__(self):
        return "Single(%s)" % self.index
