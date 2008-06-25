#!/bin/bash

testPrintVersion()
{
	./trash --version
	assertEquals 0 "$?"
}

testTrashAbsolutePath()
{
	export XDG_DATA_HOME="/tmp/temp-dir"
	rm -Rfv "$XDG_DATA_HOME/Trash"
	
        touch /tmp/dummy
	./trash /tmp/dummy
	info_content="$(<"$XDG_DATA_HOME/Trash/info/dummy.trashinfo")"
        [[ "$info_content" == "[Trash Info]
Path=/tmp/dummy
DeletionDate="* ]];
        assertEquals 0 $?
	rm -Rfv "$XDG_DATA_HOME/Trash"
}

testTrashRelativePath()
{
	export XDG_DATA_HOME="/tmp/temp-dir"
	rm -Rfv "$XDG_DATA_HOME/Trash"
	
        touch /tmp/temp-dir/dummy
	./trash /tmp/temp-dir/dummy
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
