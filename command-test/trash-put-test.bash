#!/bin/bash
# trash-put-test.bash: back box testing for trash-cli commands
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

# load common definitions
. "$(dirname "$0")/commons.bash"

setup-test-enviroment

testPrintVersion()
{
        _trash-put --version
        assertEquals 0 "$?"
}

# usage:
#   1. trash_in_home_trashcan <file>
#   2. trash_in_home_trashcan <dir>
test_trash_in_home_trashcan() {
        local expected_trashcan="$XDG_DATA_HOME/Trash"

        file_to_trash_path=(
                sandbox/trash-test/file-to-trash
                sandbox/trash-test/other-file-to-trash
                sandbox/trash-test/file-to-trash
        )

        expected_trashid=(
                file-to-trash
                other-file-to-trash
                file-to-trash_1
        )
        
        expected_path_in_trashinfo=(
                "$(pwd)/sandbox/trash-test/file-to-trash"
                "$(pwd)/sandbox/trash-test/other-file-to-trash"
                "$(pwd)/sandbox/trash-test/file-to-trash"
        )
       
        # delete trashcan
        rm -Rf "$expected_trashcan"

        for((i=0;i<${#file_to_trash_path[@]};i++));  do 
                do_trash_test "${file_to_trash_path[$i]}" "$expected_trashcan" "${expected_trashid[$i]}" "${expected_path_in_trashinfo[$i]}"
        done 

}

do_trash_test() {
        local path_to_trash="$1"
        local expected_trashcan="$2"
        local expected_trashname="$3"
        local expected_stored_path="$4"

        echo trash test informations:
        echo -e "\t"path_to_trash="$path_to_trash"
        echo -e "\t"expected_trashcan="$expected_trashcan"
        echo -e "\t"expected_trashname="$expected_trashname"
        echo -e "\t"expected_stored_path="$expected_stored_path"

        local content="$RANDOM"
        create_test_file "$content" "$path_to_trash"

        _trash-put "$path_to_trash"
        assertEquals 0 "$?"
        assert_does_not_exists "$path_to_trash"
        
        assert_trashed "$expected_trashcan" \
                       "$content" \
                       "$expected_trashname" \
                       "$expected_stored_path"

}

do_test_trash_in_volume_trashcan() {
        local expected_trashcan="$1"

        file_to_trash_path=(
                sandbox/trash-test/file-to-trash
                sandbox/trash-test/other-file-to-trash
                sandbox/trash-test/file-to-trash
        )

        expected_trashid=(
                file-to-trash
                other-file-to-trash
                file-to-trash_1
        )
        
        expected_path_in_trashinfo=(
                sandbox/trash-test/file-to-trash
                sandbox/trash-test/other-file-to-trash
                sandbox/trash-test/file-to-trash
        )

        # delete trashcan
        rm -Rf "$expected_trashcan"

        for((i=0;i<${#file_to_trash_path[@]};i++));  do 
                do_trash_test "$topdir/${file_to_trash_path[$i]}" "$expected_trashcan" "${expected_trashid[$i]}" "${expected_path_in_trashinfo[$i]}"
        done 
}


test_trash_in_volume_trashcans_when_Trash_does_not_exist() {
        rm -Rf "$topdir/.Trash"
        trashcan="$topdir/.Trash-$uid"
        do_test_trash_in_volume_trashcan "$trashcan"
}

test_trash_in_volume_trashcans_when_Trash_is_not_sticky_nor_writable() {
        rm -Rf "$topdir/.Trash"
        mkdir --parent "$topdir/.Trash"
        chmod a-t "$topdir/.Trash"        
        chmod a-w "$topdir/.Trash"
        do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_not_sticky() {
        rm -Rf "$topdir/.Trash"
        mkdir --parent "$topdir/.Trash"
        chmod a-t "$topdir/.Trash"        
        chmod a+w "$topdir/.Trash"
        do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_not_writable() {
        rm -Rf "$topdir/.Trash"
        mkdir --parent "$topdir/.Trash"
        chmod a+t "$topdir/.Trash"        
        chmod a-w "$topdir/.Trash"
        do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_ok() {
        rm -Rf "$topdir/.Trash"
        mkdir --parent "$topdir/.Trash"
        chmod +t "$topdir/.Trash"
        chmod a+w "$topdir/.Trash"
        do_test_trash_in_volume_trashcan "$topdir/.Trash/$uid"
}

prepare_volume_trashcan() {
        rm -Rf "$topdir/.Trash"
        mkdir --parent "$topdir/.Trash"
        chmod +t "$topdir/.Trash"
        chmod a+w "$topdir/.Trash"
}

get-trashed-item-count() {
        _trash-list | wc -l
}

test_trash-empty_removes_trash() {
        prepare_volume_trashcan
        _trash-empty
        assertEquals 0 "$(_trash-list | wc -l)"

        touch "$topdir/foo" "$topdir/bar" "$topdir/zap" 
        _trash-put "$topdir/foo" "$topdir/bar" "$topdir/zap"        
        assertEquals 3 "$(_trash-list | wc -l)"

        _trash-empty 
        assertEquals 0 "$(_trash-list | wc -l)"
}

test_trash-list_on_non_trashinfo_files_in_info_dir() {
        rm -Rf "$XDG_DATA_HOME/Trash"
        mkdir --parent "$XDG_DATA_HOME/Trash/info"
        touch "$XDG_DATA_HOME/info/non-trashinfo" #garbage: not ending with .trashinfo
        _trash-list
        assertEquals "$?" 0
}

test_trash-list_on_invalid_info() {
        rm -Rf "$XDG_DATA_HOME/Trash"
        mkdir --parent "$XDG_DATA_HOME/Trash/info"
        echo "An invalid trashinfo" > "$XDG_DATA_HOME/info/invalid.trashinfo"
        _trash-list
        assertEquals "$?" 0
}

. "$(dirname "$0")/bashunit.bash"
