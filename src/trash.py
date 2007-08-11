from optparse import OptionParser
from optparse import IndentedHelpFormatter

def trash (file) :
    """ 
    Trash a file in the appropriate trash directory.
    If the file belong to the same volume of the trash home directory it will
    be trashed in the home trash directory.
    Otherwise it will be trashed in one of the relevant volume trash directories.
    
    Each volume can have two trash directories, they are 
        - $volume/.Trash/$uid
        - $volume/.Trash-$uid
    
    Firstly the software attempt to trash the file in the first directory then 
    try to trash in the second trash directory.
    """
    pass

class MyFormatter (IndentedHelpFormatter) :
    def format_epilog(self, epilog):
        if epilog:
            return "\n" + epilog + "\n"
        else:
            return ""

parser = OptionParser(usage="%prog [OPTION]... FILE...",
                      description="Put files in trash",
                      version="%prog 1.0",
                      formatter=MyFormatter(),
                      epilog=
"""To remove a file whose name starts with a `-', for example `-foo',
use one of these commands:

  ${prog} -- -foo

  ${prog} ./-foo
  
Report bugs to <andreafrancia@sourceforge.net>."""
                      )
parser.add_option("-d",
                  "--directory",
                  action="store_true",
                  help="ignored (for GNU rm compatibility)")

parser.add_option("-f",
                  "--force",
                  action="store_true",
                  help="ignored (for GNU rm compatibility)")

parser.add_option("-i",
                  "--interactive",
                  action="store_true",
                  help="ignored (for GNU rm compatibility)")

parser.add_option("-r",
                  "-R",
                  "--recursive",
                  action="store_true",
                  help="ignored (for GNU rm compatibility)")

parser.add_option("-v",
                  "--verbose",
                  action="store_true",
                  help="ignored (for GNU rm compatibility)")

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("incorrect number of arguments")
