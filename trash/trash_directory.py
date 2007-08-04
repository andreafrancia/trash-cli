import os
import volume
from volume import Volume
from trash_info import TrashInfo
from trashed_file import TrashedFile

class TrashDirectory:
    def __init__(self, path) :
        self.path = path

    def trash(self, file):
        if Volume.volumeOf(self.path).sameVolume(file)==False :
            raise "file is not in the same volume of trash directory!"
        raise NotImplementedError()

    def getVolumeTrashDirectory(self, volume) :
        raise NotImplementedError()

    def getPath(self) :
        return self.path

    def getBasePath(self) :
        return volume.volumeOf(self.getPath()).getPath()

    def getInfoPath(self) :
        return os.path.join(self.getPath(), "info")

    def forEachTrashedFile(self, callMe) :
        for tf in self.getAllTrashedFile() :
            callMe(tf)
            
    def getAllTrashedFile(self) :
        list = []
        for filename in os.listdir(self.getInfoPath()) :
            infoFilename = os.path.join(self.getInfoPath(), filename)

            infoBasename = os.path.basename(infoFilename)
        
            if not infoBasename.endswith('.trashinfo') :
                raise AssertionError()
            else :
                id_ = infoBasename[:-len('.trashinfo')]
            
            ti = TrashInfo(id_)
            ti.parse(open(infoFilename).read())
            tf = TrashedFile(ti, self)
            list.append(tf)
        return list

    def getTrashedFileInDir(self, dir) :
        dir = os.path.realpath(dir)
        list = []
        for trashedfile in self.getAllTrashedFile() :
            if trashedfile.getPath().startswith(dir + os.path.sep) :
                list.append(trashedfile)
        return list

    def getOriginalCopyPath(self, id_) :
        return self.getPath() + '/files/' + str(id_)

    def removeInfoFile(self, id) :
        os.remove(self.getPath() + '/info/' + str(id) + '.trashinfo')
    
def getHomeTrashDirectory() : 
    if 'XDG_DATA_HOME' in os.environ:
        XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
    else :
        XDG_DATA_HOME = os.environ['HOME'] + '/.local/share'
        
    path = XDG_DATA_HOME + "/Trash"
    return TrashDirectory(path)

def getVolumeTrashDirectory1(volume) :
    uid = os.getuid()
    return TrashDirectory(os.path.join(volume.getPath(), ".Trash", str(uid)))

def getVolumeTrashDirectory2(volume) :
    uid = os.getuid()
    return TrashDirectory(os.path.join(volume.getPath(), ".Trash-%s" % str(uid)))

def getVolumeTrashDirectories(volume) :
    """If already exists return the volume trash directory.
    If doesn't exist yet returns None.
    See createVolumeTrashDirectory for creation of trash directory.
    """
    return [getVolumeTrashDirectory1(volume), getVolumeTrashDirectory2(volume)]

    

if __name__ == "__main__" :
    print getHomeTrashDirectory().path
    getHomeTrashDirectory().trash("/home/andrea/pippo")
    getHomeTrashDirectory().trash("/media/disk/AUTOEXEC.BAT")

