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

def get_option_parser():
    from trashcli import version
    from optparse import OptionParser
    from optparse import IndentedHelpFormatter

    class NoWrapFormatter(IndentedHelpFormatter) :
        def _format_text(self, text) :
            "[Does not] format a text, return the text as it is."
            return text

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

def main(argv=None):
    from trashcli.filesystem import Path
    from trashcli.trash import trashcan

    parser = get_option_parser()
    (options, args) = parser.parse_args(argv)

    logger = get_logger(options.verbose)

    if len(args) <= 0:
        parser.error("Please specify the files to trash.")

    for arg in args :
        f = Path(arg)
        if f.basename == '.' or f.basename == '..':
            logger.warning("cannot trash %s `%s'" % (f.type_description(), f))
        else:
            try:
                trashed_file = trashcan.trash(f)
                logger.info("`%s' trashed in %s " % (arg, trashed_file.trash_directory))
            except OSError, e:
                # occour when the file cannot be moved
                logger.warning("trash: cannot trash %s `%s': %s" % (f.type_description(), arg, str(e)))
            except IOError, e:
                # occour when the file does not exist
                logger.warning("trash: cannot trash %s `%s': %s" % (f.type_description(), arg, str(e)))