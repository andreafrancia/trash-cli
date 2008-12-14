from optparse import OptionParser

def create_option_parser():
    parser = OptionParser()
    parser.add_option("--version",
                      action="store_true",
                      help="output version information and exit",
                      dest="version")

    return parser

class RestoreCommand:
    def print_version():
        pass
    
    def restore(source, dest):
        """
        restore(source: TrashInfo, dest: Path)
        
        Restore the specified source to the specified destination.
        """
        pass
    
    def execute(self, args):
        pass

class RestoreOptionParser:
    pass