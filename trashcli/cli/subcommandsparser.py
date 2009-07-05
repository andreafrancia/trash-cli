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

# TODO: change/move this logic to a new command called SuperCommand
class SubCommandsParser():
    def __init__(self,
                 usage=None,
                 description=None,
                 version=None):
        from optparse import OptionParser

        option_parser=OptionParser()

        self.commands = {}

    def add_sub_command(self, name, command):
        self.commands[name] = command

    def parse(self, *args):
        """
        Parse the sub command and its arguments.
        """
        try :
            command = self.commands[args[0]]
            return (command, args[1:])
        except KeyError:
            raise CommandNotFoundError()
        except IndexError:
            raise CommandNotSpecifiedError()


class CommandNotFoundError(KeyError):
    pass

class CommandNotSpecifiedError(ValueError):
    pass
