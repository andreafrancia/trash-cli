import os 

class File
    def samefs(path1, path2):
	    if not (os.path.exists(path1) and os.path.exists(path2)):
	        return False

	    while path1 != os.path.dirname(path1):
	        if os.path.ismount(path1):
	            break
	        path1 = os.path.dirname(path1)

	    while path2 != os.path.dirname(path2):
	        if os.path.ismount(path2):
	            break
	        path2 = os.path.dirname(path2)

	    return path1 == path2  
		

