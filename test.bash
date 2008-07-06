#!/bin/bash

topdir=""
uid="1000"

testPrintVersion()
{
	./trash --version
	assertEquals 0 "$?"
}

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

# usage:
#  assert_is_trashed <trashcan> <original-content> <original-path> <expected_trash_name> <expected-path-for-trashinfo>
assert_is_trashed () {
    local trashcan="$1"
    local original_content="$2"
    local original_path="$3"
    local expected_trash_name="$4"
    local expected_trashinfo_path="$5"

    assertTrue "The file has been deleted?" "[ ! -e \"$original_path\" ]"

    # check that trashcan has been created
    assertTrue "Trashcan has been created?" "[ -d \"$trashcan\" ]"
    assertTrue "Trashcan contains files?"   "[ -d \"$trashcan/files\" ]"
    assertTrue "Trashcan contains info?"    "[ -d \"$trashcan/info\" ]"

    # check that the file has been trashed
    assertTrue "[ -e \"$trashcan/files/$expected_trash_name\" ]"
    assertTrue "[ -f \"$trashcan/info/$expected_trash_name.trashinfo\" ]"

    check_trashinfo "$trashcan/info/$expected_trash_name.trashinfo" "$expected_trashinfo_path"
    
    assertEquals "$original_content" "$(<$trashcan/files/$expected_trash_name)"

}

# usage:
#   1. trash_in_home_trashcan <file>
#   2. trash_in_home_trashcan <dir>
test_trash_in_home_trashcan() {
    export XDG_DATA_HOME="./test-dir"
    rm -Rf "$XDG_DATA_HOME"

    # trash a file when trashcan is not yet created 
    echo 'Hello World!' > file-to-trash
    ./trash file-to-trash

    assert_is_trashed $XDG_DATA_HOME/Trash "Hello World!" file-to-trash file-to-trash "$(pwd)/file-to-trash"

    # trash a file when trashcan is yet created 
    echo 'Hello World 2!' > other-file-to-trash
    ./trash other-file-to-trash

    assert_is_trashed $XDG_DATA_HOME/Trash "Hello World 2!" other-file-to-trash other-file-to-trash "$(pwd)/file-to-trash"

    # trash a file with the same name of already trashed file
    echo 'Hello World 3!' > file-to-trash
    ./trash file-to-trash

    assert_is_trashed $XDG_DATA_HOME/Trash "Hello World 3!" file-to-trash file-to-trash "$(pwd)/file-to-trash"

}

do_test_trash_in_volume_trashcan() {
	local trashcan="$1"

	# delete trashcan
	rm -Rf "$trashcan"

    	# trash a file when trashcan is not yet created
	echo 'Hello World!' > "/tmp/file-to-trash"
	./trash "/tmp/file-to-trash"
	assert_is_trashed "$trashcan" "Hello World!" /tmp/file-to-trash file-to-trash tmp/file-to-trash

    	# trash a file when trashcan is yet created 
    	echo 'Hello World 2!' > "/tmp/other-file-to-trash"
    	./trash "/tmp/other-file-to-trash"	
    	assert_is_trashed "$trashcan" "Hello World 2!" /tmp/other-file-to-trash other-file-to-trash tmp/other-file-to-trash

        # trash a file with the same name of already trashed file
	echo 'Hello World 3!' > "/tmp/file-to-trash"
	./trash "/tmp/file-to-trash"
	assert_is_trashed "$trashcan" "Hello World 3!" /tmp/file-to-trash file-to-trash_1 tmp/file-to-trash
}


test_trash_in_volume_trashcans_when_Trash_does_not_exist() {
	rm -Rf $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_not_sticky_nor_writable() {
	rm -Rf $topdir/.Trash
	mkdir --parent $topdir/.Trash
	chmod a-t $topdir/.Trash	
	chmod a-w $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_not_sticky() {
	rm -Rf $topdir/.Trash
	mkdir --parent $topdir/.Trash
	chmod a-t $topdir/.Trash	
	chmod a+w $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_not_writable() {
	rm -Rf $topdir/.Trash
	mkdir --parent $topdir/.Trash
	chmod a+t $topdir/.Trash	
	chmod a-w $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

test_trash_in_volume_trashcans_when_Trash_is_ok() {
	rm -Rf $topdir/.Trash
	mkdir --parent $topdir/.Trash
	chmod u+t $topdir/.Trash
	chmod a+w $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash/$uid"
}

if [  -e $topdir/.Trash ]; then
	echo "To run these test you should remove $topdir/.Trash first."
	exit
fi

# load shunit2
. test-lib/shunit2/src/shell/shunit2
