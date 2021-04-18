def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: tests that uses the filesystem"
    )
