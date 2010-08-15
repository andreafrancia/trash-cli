#!/usr/bin/python
# trashcan-admin: administer the trashcan
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

from trashcli.cli.subcommandsparser import *
from trashcli.filesystem import *
from trashcli.trash import *
from trashcli.logger import *


def main(argv=None):
    class OsFileSystem(object):
	def volumes():
	    return Volume.all()

    logger=ConsoleLogger()
    filesystem = OsFileSystem()
    trashsystem = RealTrashSystem()

    command = AdminCommand(logger, OsFileSystem(), RealTrashSystem())

    command.execute(argv)

class AdminCommand(object):
    def __init__(self, logger, filesystem, trashsystem):
        self.parser = create_command_line_parser(filesystem, logger, trashsystem)

    def execute(self, args):
        try:
            (command, args) = self.parser.parse(args)
            return command.execute(args)
        except CommandNotFoundError, e:
            logger.fatal(e)

def create_command_line_parser(filesystem, logger, trashsystem):
    import trashcli

    parser = SubCommandsParser(usage="%prog command [options] [args]",
                               description="trash-cli admin tool",
                               version="%%prog %s" % trashcli.version)

    parser.add_sub_command("list-volumes",
                           ListVolumesCommand(logger, filesystem.volumes))

    parser.add_sub_command("list-trashdirs",
                           ListTrashDirectoriesCommand(logger, trashsystem.trash_directories))

    return parser

class ListVolumesCommand(object):
    def __init__(self, logger, volume_generator):
        self.logger = logger
        self.volume_generator = volume_generator

    def execute(self, args):
        for volume in self.volume_generator():
            self.logger.reply(volume.path)

class ListTrashDirectoriesCommand(object):
    def __init__(self, logger, trash_directories_generator):
        self.logger = logger
        self.trash_directories_generator = trash_directories_generator

    def execute(self, args):
        for trashdir in self.trash_directories_generator():
            self.logger.reply("%s (%s)" % (trashdir, trashdir.volume))
