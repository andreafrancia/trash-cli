def mount_points_from_df_output(df_output):
    def skip_header():
	df_output.readline()
    def chomp(string):
	return string.rstrip('\n')
	
    result = []
    skip_header()
    for line in df_output:
	line = chomp(line)	
	yield line.split(None, 5)[-1] 

def mount_points_from_df():
    import subprocess
    df_output = subprocess.Popen(["df", "-P"], stdout=subprocess.PIPE).stdout
    return list(mount_points_from_df_output(df_output))
