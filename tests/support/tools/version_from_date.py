from __future__ import print_function

import re


def version_from_date(today):
    return "0.%s.%s.%s" % (today.year % 100,
                           today.month,
                           today.day)


def sanitize_local_version_label(value):
    return re.sub(r'[-_.]+', '.', value)


def dev_version_from_date(ref, sha, today):
    new_version = '%s.dev0+git.%s.%s' % (version_from_date(today),
                                          sanitize_local_version_label(ref),
                                          sha)
    return new_version
