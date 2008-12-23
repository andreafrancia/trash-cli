#!/bin/bash
# test.bash: back box testing for trash-cli commands
#
# Copyright (C) 2007,2008 Andrea Francia Trivolzio(PV) Italy
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

#set -o nounset
set +e
# load common definitions
. "$(dirname "$0")/commons.bash"

setup-test-enviroment

test-issue-2021948() {
        _trash-empty # delete all
        _trash-restore non-existent
        assertNotEquals $? 0
}



. "$(dirname "$0")/bashunit.bash"
