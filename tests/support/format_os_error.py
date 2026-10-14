import errno
import os


def format_os_error(e):
    return {
        "errno": str(e.errno) + " " +
                 errno.errorcode[e.errno] + " " +
                 os.strerror(e.errno) + "\n",
        "filename": e.filename + "\n",
        "args": str(e.args) + "\n",
    }
