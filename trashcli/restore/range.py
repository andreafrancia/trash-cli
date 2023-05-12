from six.moves import range


class Range:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        if self.start != other.start:
            return False
        if self.stop != other.stop:
            return False
        return True

    def __iter__(self):
        return iter(range(self.start, self.stop + 1))

    def __repr__(self):
        return "Range(%s, %s)" % (self.start, self.stop)
