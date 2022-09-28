class Suffix:
    def __init__(self, randint):
        self.randint = randint

    def suffix_for_index(self, index):
        if index == 0:
            return ""
        elif index < 100:
            return "_%s" % index
        else:
            return "_%s" % self.randint(0, 65535)
