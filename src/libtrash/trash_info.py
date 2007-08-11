import StringIO
import re
import exceptions
import urllib
from datetime import datetime
import os

class TrashInfo :
    def __init__(self, trashId = None) :
        self.id = trashId

    def setDeletionTime(self, deletionTime) :
        self.deletionTime = deletionTime

    def setPath(self, path) :
        self.path = path

    def getDeletionTimeAsString(self) :
        return datetime.strftime(self.deletionTime, "%Y-%m-%dT%H:%M:%S")

    def getDeletionTime(self) :
        return self.deletionTime

    def getPath(self) :
        return self.path

    def getId(self) :
        return self.id

    def setId(self, trashId) :
        self.id = trashId
    
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
            self.setDeletionTime(datetime.strptime(match.groups()[0], "%Y-%m-%dT%H:%M:%S"))
        except IndexError, e:
            raise ValueError()

    def render(self) :
        result = "[Trash Info]\n"
        result += "Path=" + self.getPath() + "\n"
        result += "DeletionDate=" + self.getDeletionTimeAsString() + "\n"
        return result


