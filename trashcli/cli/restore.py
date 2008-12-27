from optparse import OptionParser
from trashcli.trash import trashcan
from trashcli import version
from trashcli.cli.util import NoWrapFormatter

class RestoreCommand(object):
    def __init__(self,restorer):
        self.restorer = restorer
    
    def execute(self,args):
        parser = OptionParser(
            usage="%prog [OPTION]... FILE...",
            description=("Restore the trashed file specified by SOURCE " + 
                         "in DEST (or its original location)."),
            version="%%prog %s" % version,
            formatter=NoWrapFormatter(),
            epilog=
"""
A TrashId is a URL referring to a specific item in a specific trash directory. 
The URL has this form:

    trash:TRASH_DIR/ID

Where
    'trash:'  is the scheme part.
    TRASH_DIR is the Trash directory containing the item, can
              contains slashes '/'.
    ID        is the Item part and can not contains slashes.

The TrashId refer to the trashed file with
        TRASH_DIR/info/ID.trashinfo as .trashinfo file.
        TRASH_DIR/files/ID as original file.
""")
        parser.add_option(
            "--trash-id",
            action="store_true",
            help="The SOURCE param should be interpreted as trash ids.")
        
        parser.add_option(
            "-d",
            "--deletion-date",
            action="store_const",
            help=("Choose the trashed file with the specified original"
                  + " location and with the specified deletion date."))
        
        (options, args) = parser.parse_args(args)
        
        if len(args) == 0: 
            parser.error("Please specify the trashed file to be restored.")
        elif len(args) == 1 :
            restorer.restore_latest(args[0])
        elif len(args) == 2:
            restorer.restore_latest(args[0], args[1])
        else :
            parser.error("Too many arguments, one or two expected, %s given." 
                          % len(args))


class Restorer:
    def __init__(self, trashcan):
        self.trashcan = trashcan

    def restore_latest(self, source, dest=None):
        """
        restore(source: Path, dest: Path)
        
        Restore the specified source to the specified destination.
        """
        def is_path_equal_to_source(trashed_file):
            return trashed_file.path == source
        
        list1 = filter(is_path_equal_to_source, self.trashcan.trashed_files())
        
        latest = reduce(self.last_trashed, list1)
        latest.restore()

    @staticmethod
    def last_trashed(trashed_file1, trashed_file2):
        """
        Returns the TrashedFile more recently trashed. 
        In the case the are trashed at the same time return the first one.
        """
        if trashed_file1 == None:
            return trashed_file2
        
        if trashed_file2 == None:
            return trashed_file1
        
        if trashed_file1.deletion_date < trashed_file2.deletion_date :
            return trashed_file2
        
        if trashed_file1.deletion_date > trashed_file2.deletion_date:
            return trashed_file1
        
        return trashed_file1
    
    @staticmethod
    def both(matcher1, matcher2):
        def result(item):
            return matcher1(item) and matcher2(item)
        
        return result

def run():
    import sys
    restorer = Restorer(trashcan)
    cmd = RestoreCommand(restorer)
    cmd.execute(sys.argv[1:])