#!/bin/bash


testEquality()
{
        assertEquals 1 1
}

testPrintVersion()
{
	./trash --version
	assertEquals 0 "$?"
}

testTrashAbsolutePath()
{
	export XDG_DATA_HOME="/tmp/"
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

# load shunit2
. ./test-lib/shunit2/build/shunit2

