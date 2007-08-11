import os
import shutil

class TrashedFile :
    def __init__(self,trashinfo, trashdirectory) :
        self.__trashinfo = trashinfo
        self.__trashdirectory = trashdirectory
        
    def getPath(self) :
        return os.path.join(self.__trashdirectory.getBasePath(), self.__trashinfo.getPath())

    def getDeletionTime(self) :
        return self.__trashinfo.getDeletionTime()
 
    def restore(self) :
        if not os.path.exists(os.path.dirname(self.getPath())) :
            os.makedirs(os.path.dirname(self.getPath()))

        id_ = self.__trashinfo.getId()
        filename = self.__trashdirectory.getOriginalCopyPath(id_)
        
        shutil.move(filename, self.getPath())
        self.__trashdirectory.removeInfoFile(id_)

