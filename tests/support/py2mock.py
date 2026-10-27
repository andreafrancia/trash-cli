import sys

if sys.version_info > (3, 3):
    # noinspection PyUnusedImports
    from unittest.mock import Mock, MagicMock, call, ANY, patch
else:
    from mock import Mock, MagicMock, call, ANY, patch
