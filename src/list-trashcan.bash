
# @return 
#        0 when ok
#        1 when corrupted file
function read_trashinfo() {
	# arguments
	trashinfo_file="$1"
	trashcan_dir="$2"

	# local var
	local line
	
	# code
	cat "$trashinfo_file" | {
		line="$(line)" 
		if [[ "$line" != '[Trash Info]' ]]; then 
			echo corrupted file, 1;
			return 1;
		fi

		line="$(line)"
		if [[ "$line" != 'Path='* ]]; then 
			echo corrupted file, 2;
			return 1;
		fi
		path="${line#Path=}"
		path="$(curl_unescape "$path")"

		if [[ "${path:1:1}" == "/" ]]; then # If  path is an absolute path then 
			path="$path"
		else
			volume_of_trashcan_dir="$(volume_of "$trashcan_dir")";
			
			if [[ "${volume_of_trashcan_dir:-1:1}" == "/" ]]; then 
				path="$volume_of_trashcan_dir""$path"
			else
				path="$volume_of_trashcan_dir/$path"
			fi 
		fi
	
		line="$(line)"
		if [[ "$line" != 'DeletionDate='* ]]; then 
			echo corrupted file dt, 3;
			return 1;
		fi
		deletion_date="${line#DeletionDate=}"
		deletion_date="$(date -d "$deletion_date")"
 
	 	echo -e "$deletion_date\t$path"
	}
}


function list_trashcan_content() {
	# arguments
	trashcan_dir="$1"	# trashcan dir where search files 
	
	local trashinfo_file
	shopt -s nullglob 
	for trashinfo_file in "${trashcan_dir}"/info/*.trashinfo; do 
		read_trashinfo "$trashinfo_file" "$trashcan_dir" || true
	done
}

function enumerates_filesystems() {
#TODO: problem, \040 non gestiti
	cat /etc/mtab | cut -d " " -f 2
}

function list_all_trashcans_content() {
	list_trashcan_content "$(figure_out_home_trashcan)"
	for volume_topdir in $(enumerates_filesystems); do 
		list_trashcan_content "$volume_topdir/.Trash/$UID"
		list_trashcan_content "$volume_topdir/.Trash-$UID"
	done
}





list_all_trashcans_content



