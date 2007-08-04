import StringIO
import re
import exceptions
import urllib
import datetime
import os

class TrashInfo :
    def __init__(self, id_) :
        self.id = id_

    def setDeletionTime(self, deletionTime) :
        self.deletionTime = deletionTime

    def setPath(self, path) :
        self.path = path
    
    def getDeletionTime(self) :
        return self.deletionTime

    def getPath(self) :
        return self.path

    def getId(self) :
        return self.id
    
    def __chomp(self, string) :
        if string[-1] == '\n' :
            return string[:-1]
        else :
            return string

    def parse(self, data) :

        stream = StringIO.StringIO(data)    
        line = self.__chomp(stream.readline())
        if line != "[Trash Info]" :
            raise ValueError()

        try :
            line = self.__chomp(stream.readline())
        except :
            raise ValueError()
        
        match = re.match("^Path=(.*)$", line)
        if match == None :
            raise ValueError()
        try :
            self.setPath(urllib.unquote(match.groups()[0]))
        except IndexError, e:
            raise ValueError()
            

        try :
            line = self.__chomp(stream.readline())
        except :
            raise ValueError()
        
        match = re.match("^DeletionDate=(.*)$", line)
        if match == None :
            raise ValueError()
        try :
            self.setDeletionTime(datetime.datetime.strptime(match.groups()[0], "%Y-%m-%dT%H:%M:%S"))
        except IndexError, e:
            raise ValueError()



