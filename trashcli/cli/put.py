#!/usr/bin/python
# trash-put: put files and dirs in the trashcan
#
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trashcli.trash import *
from trashcli.filesystem import *

def main(argv=None):
    parser = get_option_parser()
    (options, args) = parser.parse_args(argv)

    if len(args) <= 0:
	parser.error("Please specify the files to trash.")

    trasher = Trasher(
	get_logger(options.verbose),
	GlobalTrashCan()
    )
    trasher.trash_all(args)

class Trasher:
    def __init__(self, logger, trashcan):
	self.logger = logger
	self.trashcan = trashcan

    def trash_all(self, args):
	for arg in args :
	    self.trash(arg)

    def trash(self, arg):
	f = Path(arg)
	if f.basename == '.' or f.basename == '..':
	    self.logger.warning("cannot trash %s `%s'" % (f.type_description(), f))
	else:
	    try:
		trashed_file = self.trashcan.trash(f)
		self.logger.info("`%s' trashed in %s " % (arg, trashed_file.trash_directory))
	    except OSError, e:
		# occour when the file cannot be moved
		self.logger.warning("trash: cannot trash %s `%s': %s" % (f.type_description(), arg, str(e)))
	    except IOError, e:
		# occour when the file does not exist
		self.logger.warning("trash: cannot trash %s `%s': %s" % (f.type_description(), arg, str(e)))


def get_option_parser():
    from trashcli import version
    from optparse import OptionParser
    from trashcli.cli.util import NoWrapFormatter

    parser = OptionParser(usage="%prog [OPTION]... FILE...",
                          description="Put files in trash",
                          version="%%prog %s" % version,
                          formatter=NoWrapFormatter(),
                          epilog=
    """To remove a file whose name starts with a `-', for example `-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to http://code.google.com/p/trash-cli/issues""")

    parser.add_option("-d",
                      "--directory",
                      action="store_true",
                      help="ignored (for GNU rm compatibility)")

    parser.add_option("-f",
                      "--force",
                      action="store_true",
                      help="ignored (for GNU rm compatibility)")

    parser.add_option("-i",
                      "--interactive",
                      action="store_true",
                      help="ignored (for GNU rm compatibility)")

    parser.add_option("-r",
                      "-R",
                      "--recursive",
                      action="store_true",
                      help="ignored (for GNU rm compatibility)")

    parser.add_option("-v",
                      "--verbose",
                      action="store_true",
                      help="explain what is being done",
                      dest="verbose")

    return parser

def get_logger(verbose):
    import sys
    from trashcli.filesystem import Path
    """
    Create a logger which sends messages to stderr filtered according to the verbosity.
    """
    import logging
    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.WARNING)
    log_stream.formatter = logging.Formatter('%(name)s: %(message)s')

    if(verbose):
        log_stream.setLevel(logging.INFO)
    else:
        log_stream.setLevel(logging.WARNING)


    logger=logging.getLogger(Path(sys.argv[0]).basename)
    logger.setLevel(logging.WARNING)
    logger.addHandler(log_stream)

    return logger

