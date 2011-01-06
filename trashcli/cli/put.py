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

from trashcli.trash import GlobalTrashCan 
from trashcli.filesystem import Path 

class TrashPutCmd:

    def __init__(self, stdout, stderr):
	self.stdout=stdout
	self.stderr=stderr

    def run(self,argv):
	parser = self.get_option_parser()
	(options, args) = parser.parse_args(argv[1:])

	if len(args) <= 0:
	    parser.error("Please specify the files to trash.")

	reporter=Reporter(self.get_logger(options.verbose,argv[0]))

	self.trashcan=GlobalTrashCan(reporter=reporter)
	self.trash_all(args)

    def trash_all(self, args):
	for arg in args :
	    self.trash(arg)

    def trash(self, arg):
	self.trashcan.trash(Path(arg))

    def get_option_parser(self):
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

    def get_logger(self,verbose,argv0):
	import os.path
	class MyLogger:
	    def __init__(self, stderr):
		self.program_name = os.path.basename(argv0)
		self.stderr=stderr
	    def info(self,message):
		if verbose:
		    self.emit(message)
	    def warning(self,message):
		self.emit(message)
	    def emit(self, message):
		self.stderr.write("{0}: {1}\n".format(self.program_name,message))
	
	return MyLogger(self.stderr)

class Reporter:
    def __init__(self, logger):
	self.logger = logger

    def unable_to_trash_dot_entries(self,file):
	self.logger.warning("cannot trash %s `%s'" % (file.type_description(), file))

    def unable_to_trash_file(self,f):
	self.logger.warning("cannot trash %s `%s'" % (f.type_description(), f))

    def file_has_been_trashed_in_as(self, trashee, trash_directory, destination):
	self.logger.info("`%s' trashed in %s " % (trashee, trash_directory))

    def unable_to_trash_file_in_because(self, file_to_be_trashed, trash_directory, error):
	self.logger.info("Failed to trash %s in %s, because :%s" % (file_to_be_trashed,
	    trash_directory, error))

def main():
    import sys
    cmd=TrashPutCmd(sys.stdout,sys.stderr)
    cmd.run(sys.argv)

