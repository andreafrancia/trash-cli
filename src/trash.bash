

# Create a pathkey for trashinfo file according to XDG Trash specification.
function create_path_key() {
        local path="$1"
        local trashcan_directory="$2"

        dirname_of_path="$(dirname "$path")"
        basename_of_path="$(basename "$path")"
        absolute_path="$(realpath "$dirname_of_path")/$basename_of_path"

        trashcan_directory="$(realpath "$trashcan_directory")"
        trashcan_directory_volume="$(volume_of "$trashcan_directory")"
        relative_path="${absolute_path#"$trashcan_directory_volume"}"
        
	echo "$relative_path"
}


function prepare_trash_information_content() {
	local file_to_trash="$1"
	local trashcan_directory="$2"

	local deletion_date_line="$(date +%Y-%m-%dT%H:%M:%S)"
	local path_key_value="$(create_path_key "$file_to_trash" "$trashcan_directory")"
	
	echo "[Trash Info]
Path="$(curl_escape "$path_key_value")"
DeletionDate="$deletion_date_line"
"
}


function scrivi_in_modo_atomico () {
	local filename="$1"
	local content="$2"

	if atomic_create "$filename"; then	
		echo "$content" > "$filename"
	else
		return 1
	fi

	return 0;
}

function negotiate_trashinfo() {
	local trashcan_directory="$1"
	local trashname_prefix="$2"
	local trashinfo_content="$3"
	
	local successful_creation=false
	
	local -i i
	local path_for_trashinfo
	for ((i=0;i<10;i++)); do 
		local filename
		filename="${trashcan_directory}/info/${trashname_prefix}_${RANDOM}_${i}.trashinfo"
		if scrivi_in_modo_atomico "$filename" "$trashinfo_content"; then 
                	successful_creation=true
			path_for_trashinfo="$filename"
			break #exit from for
              	fi
	done

	if [[ successful_creation = false ]]; then 
              	echo "wasn't not able to create trashinfo file, (%i tries)." >2
	      	return 1
	else
		echo "$path_for_trashinfo"
		return 0
	fi

}


#that return path_where_store_trashed_file
function calc_path_for_original_copy () {
	local path_for_trashinfo="$1"
	local trashcan_directory="$2"

	#e.g. values
	# path_for_trashinfo=/home/andrea/.local/share/Trash/info/deleted_123.trashinfo
	# trashcan_directory=/home/andrea/.local/share/Trash
	
	local a="${trashcan_directory}/info/"		# a=/home/andrea/.local/share/Trash/info/
	local b="${path_for_trashinfo#$a}"		# b=deleted_123.trashinfo
	local c="${b%.trashinfo}"			# c=deleted_123
	echo "$trashcan_directory/files/$c"		# /home/andrea/.local/share/Trash/files/deleted_123
}

function move_original_file_in_trashcan () {
	local path_where_store_trashed_file="$1"
	local file_to_trash="$2"
	
	mv --force "$file_to_trash" "$path_where_store_trashed_file"
	if [[ $? -ne 0 ]]; then
     		error_msg="Unable to move file in trashcan"
	fi
}

function try_trash_file_in_trashcan() {
	local file_to_trash="$1"
	local trashcan_directory="$2"

	mkdir --parents "$trashcan_directory"
	mkdir --parents "$trashcan_directory/files"
	mkdir --parents "$trashcan_directory/info"

	local content="$(prepare_trash_information_content "$file_to_trash" "$trashcan_directory" )"
	local trashname_prefix="$(basename "$file_to_trash")_"
	
	local path_for_trashinfo="$(negotiate_trashinfo "$trashcan_directory" "$trashname_prefix" "$content")"
	if [[ "$?" -ne 0 ]]; then
		return 1
	else 
		local path_where_store_trashed_file="$(calc_path_for_original_copy "$path_for_trashinfo" "$trashcan_directory")"
		if [[ "$?" -ne 0 ]]; then
			# rollback
			rm -f "$path_for_trashinfo"
			return 1
		else
			move_original_file_in_trashcan "$path_where_store_trashed_file" "$file_to_trash"
			if [[ "$?" -ne 0 ]]; then
				# rollback
				rm -f "$path_for_trashinfo"
				return 1
			else 
				return 0
			fi
		fi
	fi
}


function choose_and_try_trashcans() {
	local home_trashcan="$1"
	local file_to_trash="$2"
	local uid="$3"

	local result
        local volume # volume top dir of volume owning file to be trashed
        
        volume="$(volume_of "$file_to_trash")"
        
	if  [[ "$volume" == "$(volume_of home_trashcan)" ]]; then 
                try_trash_file_in_trashcan "$file_to_trash" "$home_trashcan"
                result="$?"
        else
		result=1
		
		if volume_has_method1trashcan "$volume"; then
			try_trash_file_in_trashcan "$file_to_trash" "$volume/.Trash/$uid"	
                        result="$?"
		fi

                if [[ $result -ne 0 ]]; then 
			try_trash_file_in_trashcan "$file_to_trash" "$volume/.Trash-$uid"
                        result="$?"
		fi
		
                if [[ $result -ne 0 ]]; then 
                        try_trash_file_in_trashcan "$file_to_trash" "$home_trashcan"
                        result="$?"
		fi
	fi
	
        return "$result"
}

function trash_a_file() {
	local file_to_trash="$1"
	
	local home_trashcan="$(figure_out_home_trashcan)"

	choose_and_try_trashcans "$home_trashcan"  "$file_to_trash" "$UID"

	return "$?"
}

function trash_files () {
	local result=0
	for file_to_trash in "$@"; do 
		if [[ -e "$file_to_trash" ]]; then
			trash_a_file "$file_to_trash"
        	        if [[ "$result" -ne 0 ]]; then 
				result=1
			fi
		else 
			return 1
		fi
	done
	return "$result"
}


prog="$(basename "${0}")"
purpose="Put files in trash"

function license () {
echo "# ${prog} ${version} -- ${purpose}
#  

# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any
# later version.

# This is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the file
# /usr/share/common-licenses/GPL for more details."
}

function show_version () {
	echo "${prog} version ${VERSION} -- ${purpose}";
}


function usage () {
	echo "Usage: ${prog} [OPTION]... FILE...
  ${purpose}
 
  -d, --directory       ignored (for GNU rm compatibility)
  -f, --force           ignored (for GNU rm compatibility)
  -i, --interactive     ignored (for GNU rm compatibility)
  -r, -R, --recursive   ignored (for GNU rm compatibility)
  -v, --verbose         explain what is being done
      --help            display this help and exit
      --version         output version information and exit

To remove a file whose name starts with a \`-\', for example \`-foo\',
use one of these commands:
  ${prog} -- -foo

  ${prog} ./-foo

Report bugs to <andreafrancia@sourceforge.net>."  
}




if `getopt -T >/dev/null 2>&1` ; [ $? != 4 ] ; then
	echo "Sorry, this script work only with GNU getopt version" >&2
	echo "Terminating" >&2
 	exit 1
fi

if [ $# -eq 0 ]; then usage; exit 0; fi;

# Note that we use `"$@"' to let each command-line parameter expand to a 
# separate word. The quotes around `$@' are essential!
# We need TEMP as the `eval set --' would nuke the return value of getopt.
LONG_OPTS="directory,force,interactive,recursive,verbose,help,version"
TEMP=$(getopt -o dfvirR --long $LONG_OPTS \
     -n $(basename $0) -- "$@" )

if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do  
	case "$1" in
		-d|--directory) options="${options}d"; shift ;; 
		-f|--force) options="${options}f"; shift ;; 
		-i|--interactive) options="${options}i"; shift ;; #ignored
		-r|-R|--recursive) options="${options}rR"; shift ;; 
                -v|--verbose) options="${options}v"; shift ;; 
                --help) usage ; exit 0; shift ;;
                --version) show_version; exit 0; shift ;;
		--) shift ; break ;;
		*) echo "Internal error!" ; exit 1 ;;
	esac
done

trash_files "$@"

