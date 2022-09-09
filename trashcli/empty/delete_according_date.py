from trashcli.empty.older_than import older_than
from trashcli.trash import parse_deletion_date


class ContentReader:
    def contents_of(self, path):
        raise NotImplementedError


class DeleteAccordingDate:
    def __init__(self,
                 reader,  # type: ContentReader
                 clock,
                 max_age_in_days):
        self.reader = reader
        self.clock = clock
        self.max_age_in_days = max_age_in_days

    def ok_to_delete(self, trashinfo_path):
        contents = self.reader.contents_of(trashinfo_path)
        now_value = self.clock.get_now_value()
        deletion_date = parse_deletion_date(contents)
        if deletion_date is not None:
            if older_than(self.max_age_in_days, now_value, deletion_date):
                return True
        return False
