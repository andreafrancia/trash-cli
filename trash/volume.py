import os

class Volume : 
    def __init__(self,path):
        if os.path.ismount(path) :        
            self.path = path
        else:
            raise "path is not a mount point"
    
    def sameVolume(self,path) : 
        return volumeOf(path).path == self.path

    def getPath(self) :
        return self.path


def volumeOf(path) : 
    path = os.path.realpath(path)
    while path != os.path.dirname(path):
        if os.path.ismount(path):
	        break
        path = os.path.dirname(path)
    return Volume(path)

"""
mount_list
Taste the system and return a list of mount points.
On UNIX this will return what a df will return
On DOS based systems run through a list of common drive letters and
test them
to see if a mount point exists. Whether a floppy or CDROM on DOS is
currently active may present challenges.
Curtis W. Rendon 6/27/200 v.01
  6/27/2004 v.1 using df to make portable, and some DOS tricks to get
active
drives. Will try chkdsk on DOS to try to get drive size as statvfs()
doesn't exist on any system I have access to...

"""
import sys,os,string
from stat import *

def mount_list():
  """
  returns a list of mount points
  """


  doslist=['a:\\','b:\\','c:\\','d:\\','e:\\','f:\\','g:\\','h:\\','i:\\','j:\\','k:\\','l:\\','m:\\','n:\\','o:\\','p:\\','q:\\','r:\\','s:\\','t:\\','u:\\','v:\\','w:\\','x:\\','y:\\','z:\\']
  mount_list=[]

  """
  see what kind of system
  if UNIX like
     use os.path.ismount(path) from /... use df?
  if DOS like
     os.path.exists(path) for  a list of common drive letters
  """
  if sys.platform[:3] == 'win':
    #dos like
    doslistlen=len(doslist)
    for apath in doslist:
      if os.path.exists(apath):
        #maybe stat check first... yeah, it's there...
        if os.path.isdir(apath):
          mode = os.stat(apath)
          try:
             dummy=os.listdir(apath)
             mount_list.append(apath)
          except:
             continue
        else:
          continue
    return (mount_list)

  else:
    #UNIX like
    """
    AIX and SYSV are somewhat different than the GNU/BSD df, try to catch
    them. This is for AIX, at this time I don't have a SYS5 available to see
    what the sys.platform returns... CWR
    """
    if 'aix' in sys.platform.lower():
      df_file=os.popen('df')
      while True:
        df_list=df_file.readline()
        if not df_list:
          break #EOF
        dflistlower = df_list.lower()
        if 'filesystem' in dflistlower:
          continue
        if 'proc' in dflistlower:
          continue

        file_sys,disc_size,disc_avail,disc_cap_pct,inodes,inodes_pct,mount=df_list.split()
        mount_list.append(mount)

    else:
      df_file=os.popen('df')
      while True:
        df_list=df_file.readline()
        if not df_list:
          break #EOF
        dflistlower = df_list.lower()
        if 'filesystem' in dflistlower:
          continue
        if 'proc' in dflistlower:
          continue

        file_sys,disc_size,disc_used,disc_avail,disc_cap_pct,mount=df_list.split()
        mount_list.append(mount)

    return (mount_list)


def all() :
    return [ Volume(elem) for elem in mount_list()]



if __name__ == "__main__" :
    print volumeOf("/home/andrea/Documenti/ecchi").path
    print all()

