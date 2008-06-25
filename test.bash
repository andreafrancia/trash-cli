#!/bin/bash

testPrintVersion()
{
	./trash --version
	assertEquals 0 "$?"
}

testTrashAbsolutePath()
{
	export XDG_DATA_HOME="./test-dir"
	rm -Rfv "$XDG_DATA_HOME/Trash"
	
        touch dummy
	./trash dummy
        
        dummy_fullpath="$(pwd)"/dummy
	
        info_content="$(<"$XDG_DATA_HOME/Trash/info/dummy.trashinfo")"

        info_content_line_1="$(echo "$info_content" | sed -n '1p' )"
        info_content_line_2="$(echo "$info_content" | sed -n '2p' )"
        info_content_line_3="$(echo "$info_content" | sed -n '3p' )"
 
        assertEquals "[Trash Info]" "$info_content_line_1"
        assertEquals "Path=$dummy_fullpath" "$info_content_line_2"
        assertTrue "DeletionDate problem" '[[ '"$info_content_line_3"' == DeletionDate=????-??-??T??:??:?? ]]'

	rm -Rfv "$XDG_DATA_HOME/Trash"
}

testTrashRelativePath()
{
	export XDG_DATA_HOME="./test-dir"
	rm -Rfv "$XDG_DATA_HOME/Trash"
	
        touch ./test-dir/dummy
	./trash ./test-dir/dummy
	info_content="$(<"$XDG_DATA_HOME/Trash/info/dummy.trashinfo")"

        info_content_line_1="$(echo "$info_content" | sed -n '1p' )"
        info_content_line_2="$(echo "$info_content" | sed -n '2p' )"
        info_content_line_3="$(echo "$info_content" | sed -n '3p' )"
        
        assertEquals "[Trash Info]" "$info_content_line_1"
        assertEquals "Path=dummy" "$info_content_line_2"
        assertTrue "DeletionDate problem" '[[ '"$info_content_line_3"' == DeletionDate=????-??-??T??:??:?? ]]'

	rm -Rfv "$XDG_DATA_HOME/Trash"
}


# load shunit2
. test-lib/shunit2/src/shell/shunit2
