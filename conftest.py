import os

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: tests that uses the filesystem"
    )


@pytest.fixture(scope="session")
def process_umask():
    current = os.umask(0)
    os.umask(current)
    return current
