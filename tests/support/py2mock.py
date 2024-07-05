import sys

if sys.version_info > (3, 3):
    from unittest.mock import *
else:
    from mock import *
