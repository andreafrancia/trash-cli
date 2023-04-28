from __future__ import absolute_import

import datetime


class Clock:
    def __init__(self, real_now, errors):
        self.real_now = real_now
        self.errors = errors

    def get_now_value(self, environ):
        if 'TRASH_DATE' in environ:
            try:
                return datetime.datetime.strptime(environ['TRASH_DATE'],
                                                  "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                self.errors.print_error('invalid TRASH_DATE: %s' %
                                        environ['TRASH_DATE'])
                return self.real_now()
        return self.real_now()
