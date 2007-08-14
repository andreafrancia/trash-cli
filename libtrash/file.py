import os 
import shutil
import volume

class File :
    def __init__(self, path) :
        self.path = os.path.abspath(path)

    def getParent(self) :
        return File(os.path.dirname(self.path))
    
    def getRealParent(self) :
        return File(os.path.realpath(os.path.dirname(self.path)))
    
    def getBasename(self) :
        return os.path.basename(self.path)

    def move(self, dest) :
        return shutil.move(self.path, dest)
    
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
    
    def getVolume(self) :
        return volume.volumeOf(self.path)

    def getPath(self) :
        return self.path

    def remove(self) :
        return os.remove(self.path)
