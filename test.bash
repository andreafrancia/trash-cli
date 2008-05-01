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
        [[ "$info_content" == "[Trash Info]
Path=dummy
DeletionDate="* ]];
        assertEquals 0 $?
	rm -Rfv "$XDG_DATA_HOME/Trash"
}


# build and load shunit2
pushd ./test-lib/shunit2/
make
popd
. ./test-lib/shunit2/build/shunit2

