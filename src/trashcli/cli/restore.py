from optparse import OptionParser

def create_option_parser():
    parser = OptionParser()
    parser.add_option("--version",
                      action="store_true",
                      help="output version information and exit",
                      dest="version")

    return parser

class RestoreCommand:
    def print_version(self):
        pass
    
    def restore(self, source, dest):
        """
        restore(source: TrashInfo, dest: Path)
        
        Restore the specified source to the specified destination.
        """
        pass
    
    def execute(self, args):
        pass

class RestoreOptionParser:
    pass

def extract(source, matches):
    """
    source: generator or list.
    matches: the matches function. matches(item) should return True if item matches, False otherwise
    return 
    """
    for item in source:
        if matches(item):
            yield item
            
def last_trashed(trashed_file1, trashed_file2):
    """Returns the TrashedFile more recently trashed. 
    In the case the are trashed at the same time return the first one.
    """
    if trashed_file1.deletion_date < trashed_file2.deletion_date :
        return trashed_file2
    elif trashed_file1.deletion_date > trashed_file2.deletion_date:
        return trashed_file1
    else :
        return trashed_file1
        