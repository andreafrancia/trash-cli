from typing import Callable

from trashcli.lib.my_input import Input
from trashcli.restore.my_range import my_range
from trashcli.restore.range import Range
from trashcli.restore.sequences import Sequences
from trashcli.restore.single import Single


class RestoreAskingTheUser(object):
    def __init__(self,
                 input, # type: Input
                 println,  # type: Callable[[str], None]
                 restorer,
                 die, # type: Callable[[str], None]
                 ):
        self.input = input
        self.println = println
        self.restorer = restorer
        self.die = die

    def restore_asking_the_user(self, trashed_files, overwrite=False):
        try:
            user_input = self.input.read_input(
                "What file to restore [0..%d]: " % (len(trashed_files) - 1))
        except KeyboardInterrupt:
            return self.die("")
        except EOFError:
            return self.die("")
        if user_input == "":
            self.println("Exiting")
        else:
            try:
                sequences = parse_indexes(user_input, len(trashed_files))
            except InvalidEntry as e:
                self.die("Invalid entry: %s" % e)
            else:
                try:
                    for index in sequences.all_indexes():
                        trashed_file = trashed_files[index]
                        self.restorer.restore_trashed_file(trashed_file, overwrite)
                except IOError as e:
                    self.die(e)


class InvalidEntry(Exception):
    pass


def parse_indexes(user_input, len_trashed_files):
    indexes = user_input.split(',')
    sequences = []
    for index in indexes:
        if "-" in index:
            first, last = index.split("-", 2)
            if first == "" or last == "":
                raise InvalidEntry("open interval: %s" % index)
            split = list(map(parse_int_index, (first, last)))
            sequences.append(Range(split[0], split[1]))
        else:
            index = parse_int_index(index)
            sequences.append(Single(index))
    result = Sequences(sequences)
    acceptable_values = my_range(0, len_trashed_files)
    for index in result.all_indexes():
        if not index in acceptable_values:
            raise InvalidEntry(
                "out of range %s..%s: %s" %
                (acceptable_values[0], acceptable_values[-1], index))
    return result


def parse_int_index(text):
    try:
        return int(text)
    except ValueError:
        raise InvalidEntry("not an index: %s" % text)
