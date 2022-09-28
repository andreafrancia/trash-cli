class TrashResult:
    def __init__(self, some_file_has_not_be_trashed):
        self.some_file_has_not_be_trashed = some_file_has_not_be_trashed

    def mark_unable_to_trash_file(self):
        return TrashResult(True)

    def __eq__(self, other):
        return self.some_file_has_not_be_trashed == \
               other.some_file_has_not_be_trashed

    def __repr__(self):
        return 'TrashResult(%s)' % self.some_file_has_not_be_trashed
