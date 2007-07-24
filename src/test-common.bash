#!/bin/bash
source common.bash

function volume_of_using_df_command() {
	local filepath="$1"

	dirname="$(realpath "$(dirname "$filepath")")" 
        # determine volume and get relative path
        volume="$(df -- "$dirname")" # get volume info
                                     # e.g:
                                     # "Filesystem Size Used Avail Use% Mounted on
                                     # /dev/hda10 2,8G 2,3G 418M 85% /home"
        volume="${volume##* }" # get the last field, volume name ("Mounted On")
                               # e.g.: "/var"
	echo "$volume"
}



test_volume_of() {
	testcases=( /proc / /proc/ /proc/fs/ /home )
	for i in "${testcases[@]}"; do 
		echo "$i: $(volume_of "$i") -vs- $(volume_of_using_df_command "$i")"
	done;
}



test_volume_of

