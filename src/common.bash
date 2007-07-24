#!/bin/bash

# determine the volume of a file and prints it out
# BUGS: it is not able to parse \040 value in /etc/mtab, the ANSI C getmntent 
#  function does this.
function volume_of() {
	#function arguments
	local filepath="$1"

	#local variables
	local dirname

	dirname="$(realpath "$(dirname "$filepath")")" 
        if [[ "${dirname:-1:1}" != "/" ]]; then 
		# add a slash to string
	        dirname="$dirname/" 
        fi
	
	# search in each volume the best volume_of $filepath.
	local best_found="";

	volumes=( $(cat /etc/mtab  | cut -d " " -f 2) )
	for fs in "${volumes[@]}"; do 
		
        	# make sure that a slash at the end of the string
	        # if last char it isn't a "/"
        	if [[ "${fs:-1:1}" != "/" ]]; then 
	                # add a slash to string
		        fs_wslash="$fs/" 
		else 
			fs_wslash="$fs"
	        fi
		
	 	# using a terminating slash is essential for don't make mistake
	        # like /mnt/cdrom = /mnt/cdrom1/pippo
        	if [[  "$dirname" == "$fs_wslash"*  ]]; then
			# this volume matches
	
			# is better than previous matching volume?
			# the better is the longest in name
	
		        # if this volume is longer of $best_matching_volume_found       
			# note: the value of ${#var} is the lenght of string $var
			if [[ "${#fs}" -gt "${#best_found}" ]]; then
				#then is better
				best_found="$fs";
			fi

		fi
	done
	echo "$best_found"
}



function volume_has_method1trashcan() {
	local volume_topdir="$1"
	
	# checks required by trash specification (from http://www.ramendik.ru/docs/trashspec.0.7.html)
	# 1. check if $topdir/.Trash exist
	# 2. check if $topdir/.Trash is a directory
	# 3. check if $topdir/.Trash is not a symbolic link
	# 4. check it $topdir/.Trash has sticky bit
	
	test -e "$volume_topdir/.Trash" || return 1
        test -d "$volume_topdir/.Trash" || return 1
	test ! -L "$volume_topdir/.Trash" || return 1
	test -k "$volume_topdir/.Trash" || return 1
	return 0
}




function figure_out_home_trashcan() {
	echo "${XDG_DATA_HOME:-"$HOME/.local/share"}/Trash"
}


