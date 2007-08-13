import os

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

        trashId = self.__trashinfo.getId()
        self.__trashdirectory.getOriginalCopy(trashId).move(self.getPath())
        self.__trashdirectory.getInfoFile(trashId).remove()

