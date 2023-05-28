from trashcli.empty.clock import Clock
from trashcli.empty.older_than import older_than
from trashcli.fs import ContentsOf
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date


class DeleteAccordingDate:
    def __init__(self,
                 reader,  # type: ContentsOf
                 clock,  # type: Clock
                 ):
        self.reader = reader
        self.clock = clock

    def ok_to_delete(self, trashinfo_path, environ,
                     parsed_days):  # type: (str, dict, int) -> bool
        if parsed_days is None:
            return True
        else:
            contents = self.reader.contents_of(trashinfo_path)
            now_value = self.clock.get_now_value(environ)
            deletion_date = parse_deletion_date(contents)
            if deletion_date is not None:
                if older_than(parsed_days, now_value, deletion_date):
                    return True
            return False
