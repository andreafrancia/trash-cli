#!/bin/bash
# common.bash: Utility function for testing trash-cli commands
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

topdir="$(pwd)/test-volume"

uid="$(python -c "import os; 
try: 
    print os.getuid()
except AttributeError: 
    print 0")"

# --- commands --------------------------------------------
_trash-put() {
        echo "Invoking: trash $@" 1>&2
        ../scripts/trash-put "$@"
}

_trash-empty() {
        echo "Invoking: trash-empty $@" 1>&2
        ../scripts/trash-empty "$@"
}

_trash-list() {
        echo "Invoking: trash-list $@" 1>&2
        ../scripts/trash-list "$@"
}

_trash-restore() {
        echo "Invoking: trash-restore $@" 1>&2
        ../scripts/trash-restore "$@"
}

_restore-trash() {
        echo "Invoking: restore-trash $@" >2
        ../scripts/restore-trash "$@"
}
# --- end of commands --------------------------------------

# Usage:
#   check_trashinfo <path-to-trashinfo> <expected-path>
# Description:
#   Check that the trashinfo file contains the expected information
check_trashinfo() {
        local trashinfo="$1"
        local expected_path="$2"

        assertEquals 3 "$(wc -l <$trashinfo)"

        local line1="$(sed -n '1p'< "$trashinfo")"
        local line2="$(sed -n '2p'< "$trashinfo")"
        local line3="$(sed -n '3p'< "$trashinfo")"

        assertEquals "[Trash Info]" "[Trash Info]" "$line1"
        assertEquals "Path" "Path=$expected_path" "$line2"
        assertTrue "DeletionDate" '[[ '"$line3"' == DeletionDate=????-??-??T??:??:?? ]]'
}

assert_does_not_exists() {
        local path="$1"
        assertTrue "[ ! -e \"$path\" ]" 
}

# usage:
#  assert_trashed <trashcan> <expected_content> <expected_trash_name> <expected_trashinfo_path>
assert_trashed () {
        local trashcan="$1"
        local expected_content="$2"
        local expected_trash_name="$3"
        local expected_trashinfo_path="$4"

        # check that trashcan has been created
        assertTrue "[ -d \"$trashcan\" ]"
        assertTrue "[ -d \"$trashcan/files\" ]"
        assertTrue "[ -d \"$trashcan/info\" ]"

        # check that the file has been trashed
        assertTrue "[ -e \"$trashcan/files/$expected_trash_name\" ]"
        assertTrue "[ -f \"$trashcan/info/$expected_trash_name.trashinfo\" ]"

        check_trashinfo "$trashcan/info/$expected_trash_name.trashinfo" "$expected_trashinfo_path"

        assertEquals "$expected_content" "$(<$trashcan/files/$expected_trash_name)"
}


# Usage:
#    create_test_file <content> <path>
# TODO: rename create-file
create_test_file() {
        local content="$1"
        local path="$2"

        mkdir --parents "$(dirname "$path")"
        echo "$content" > "$path"
        
        assertTrue "[ -e \"$path\" ]"
        assertEquals "$content" "$(<$path)"       
}

# Usage:
#    create-trashed-file <path> [<content>]
#
# Creates a file in the specified <path> with the specified <content> and 
# trashes it.
create-trashed-file() {
        path="$1"
        content="${2:-}"
        
        create_test_file "$content" "$path"
        
        _trash-put "$path"
        assertTrue "[ ! -e \"$path\" ]"
}

prepare_volume_trashcan() {
        rm -Rf $topdir/.Trash
        mkdir --parent $topdir/.Trash
        chmod u+t $topdir/.Trash
        chmod a+w $topdir/.Trash
}

get-trashed-item-count() {
        _trash-list | wc -l
}

setup-test-enviroment() {
        if [ -e $topdir/not-mounted ]; then
                echo "test volume not mounted, please run:"
                echo "    bash command-test/mount-test-volume.sh"
                exit 
        fi

        if [ ! -e $topdir ]; then
                echo "Please choose a topdir that exists."
                exit
        fi
        
        rm -Rf $topdir/.Trash
        rm -Rf $topdir/.Trash-$uid        
}

