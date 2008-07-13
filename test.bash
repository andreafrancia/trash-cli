#!/bin/bash
#set -o nounset

topdir="/media/disk"
uid="$(python -c "import os; print os.getuid()")"

invoke_trash() 
{
	echo "Invoking: trash $@"
	./trash $@
}


testPrintVersion()
{
	invoke_trash --version
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

# usage:
#   1. trash_in_home_trashcan <file>
#   2. trash_in_home_trashcan <dir>
test_trash_in_home_trashcan() {
        export XDG_DATA_HOME="./test-dir"
        local expected_trashcan="$XDG_DATA_HOME/Trash"

        file_to_trash_path=(
                trash-test/file-to-trash
                trash-test/other-file-to-trash
                trash-test/file-to-trash
        )

        expected_trashid=(
                file-to-trash
                other-file-to-trash
                file-to-trash_1
        )
        
        expected_path_in_trashinfo=(
                "$(pwd)/trash-test/file-to-trash"
                "$(pwd)/trash-test/other-file-to-trash"
                "$(pwd)/trash-test/file-to-trash"
        )
       
	# delete trashcan
	rm -Rf "$expected_trashcan"

        for((i=0;i<${#file_to_trash_path[@]};i++));  do 
                do_trash_test "${file_to_trash_path[$i]}" "$expected_trashcan" "${expected_trashid[$i]}" "${expected_path_in_trashinfo[$i]}"
        done 

}

# Usage:
#    create_test_file <content> <path>
create_test_file() {
        local content="$1"
        local path="$2"

        mkdir --parents "$(dirname "$path")"
        echo "$content" > "$path"
}

do_trash_test() {
        local path_to_trash="$1"
        local expected_trashcan="$2"
        local expected_trashname="$3"
        local expected_stored_path="$4"
        
        local content="$RANDOM"
        create_test_file "$content" "$path_to_trash"

        invoke_trash "$path_to_trash"
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
                trash-test/file-to-trash
                trash-test/other-file-to-trash
                trash-test/file-to-trash
        )

        expected_trashid=(
                file-to-trash
                other-file-to-trash
                file-to-trash_1
        )
        
        expected_path_in_trashinfo=(
                trash-test/file-to-trash
                trash-test/other-file-to-trash
                trash-test/file-to-trash
        )

	# delete trashcan
	rm -Rf "$expected_trashcan"

        for((i=0;i<${#file_to_trash_path[@]};i++));  do 
                do_trash_test "$topdir/${file_to_trash_path[$i]}" "$expected_trashcan" "${expected_trashid[$i]}" "${expected_path_in_trashinfo[$i]}"
        done 
}


test_trash_in_volume_trashcans_when_Trash_does_not_exist() {
	rm -Rf $topdir/.Trash
        trashcan="$topdir/.Trash-$uid"
	do_test_trash_in_volume_trashcan "$trashcan"
}

dont_test_trash_in_volume_trashcans_when_Trash_is_not_sticky_nor_writable() {
	rm -Rf $topdir/.Trash
	mkdir --parent $topdir/.Trash
	chmod a-t $topdir/.Trash	
	chmod a-w $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

dont_test_trash_in_volume_trashcans_when_Trash_is_not_sticky() {
	rm -Rf $topdir/.Trash
	mkdir --parent $topdir/.Trash
	chmod a-t $topdir/.Trash	
	chmod a+w $topdir/.Trash
	do_test_trash_in_volume_trashcan "$topdir/.Trash-$uid"
}

dont_test_trash_in_volume_trashcans_when_Trash_is_not_writable() {
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

if [ ! -e $topdir ]; then
	echo "Please choose a topdir that exists."
	exit
fi

if [  -e $topdir/.Trash  -o -e $topdir/.Trash-$uid ]; then
	echo "To run these test you should remove these directories first."
        echo " - $topdir/.Trash "
        echo " - $topdir/.Trash-$uid "
	exit
fi

# load shunit2
. test-lib/shunit2/src/shell/shunit2

