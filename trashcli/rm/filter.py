# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import fnmatch
import os


class Filter:
    def __init__(self, pattern):
        self.pattern = pattern

    def matches(self, original_location):
        basename = os.path.basename(original_location)
        # a pattern that starts with / matches the full original path
        subject = original_location if self.pattern.startswith('/') \
            else basename
        return fnmatch.fnmatchcase(subject, self.pattern)
