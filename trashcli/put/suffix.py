from trashcli.put.core.int_generator import IntGenerator


class Suffix:
    def __init__(self,
                 int_gen,  # type: IntGenerator
                 ):
        self.int_gen = int_gen

    def suffix_for_index(self, index):
        if index == 0:
            return ""
        elif index < 100:
            return "_%s" % index
        else:
            return "_%s" % self.int_gen.new_int(0, 65535)
