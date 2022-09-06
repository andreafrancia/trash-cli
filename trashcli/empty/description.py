def description(program_name, printer):
    printer.usage('Usage: %s [days]' % program_name)
    printer.summary('Purge trashed files.')
    printer.options(
        "  --version   show program's version number and exit",
        "  -h, --help  show this help message and exit")
    printer.bug_reporting()
