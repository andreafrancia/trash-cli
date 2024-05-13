from __future__ import print_function


def version_from_date(today):
    return "0.%s.%s.%s" % (today.year % 100,
                           today.month,
                           today.day)


def dev_version_from_date(ref, sha, today):
    new_version = '%s.dev0+git.%s.%s' % (version_from_date(today), ref, sha)
    return new_version
