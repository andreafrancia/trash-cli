#!/bin/bash
# test.bash: back box testing for trash-cli commands
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

#set -o nounset
set +e
# load common definitions
. "$(dirname "$0")/commons.bash"

setup-test-enviroment

test-restore-trash-with-non-existent-trash() {
        _trash-empty # delete all
        _trash-restore non-existent
        assertNotEquals $? 0
}

test-restore-trash() {
        # prepare
        _trash-empty # delete all
        touch file
        _trash-put file
        
        # execute
        assertThat "[ ! -e file ]"
        _trash-restore file 
        
        # test
        assertEquals 0 $?
        assertThat "[ -e file ]" 
}

test-restore-trash-creates-dirs() {
        # prepare
        _empty-trash # delete all
        create-trashed-file dir/file
        rmdir dir
        assertTrue "[ ! -e dir ]" 
        
        # execute        
        _trash-restore dir/file
        
        # test
        assertEquals 0 $?
        assertTrue "[ -e dir/file ]" 
}

test-restore-trash-restores-in-dir() {
        # prepare
        _trash-empty # delete all
        create-trashed-file dir/file
        rmdir dir
        assertTrue "[ ! -e dir ]" 
        
        # execute        
        _trash-restore dir/file
        
        # test
        assertEquals 0 $?
        assertTrue "[ -e dir/file ]" 
}

test-restore-trash-restores-the-latest-deleted() {
        # prepare
        _empty-trash # delete all
        create-trashed-file file "not the latest deleted"
        create-trashed-file file "the latest deleted"
        
        # execute        
        _trash-restore file
        
        # test
        assertEquals 0 $?
        assertTrue "[ -e file ]" 
        assertEquals "the latest deleted" "$(<file)"
}



. "$(dirname "$0")/bashunit.bash"
