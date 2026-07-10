import sys

if sys.version_info > (3, 3):
    # noinspection PyUnusedImports
    from unittest.mock import *
else:
    from mock import *
