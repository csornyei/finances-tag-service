import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_env_variables():
    """
    Set environment variables for all tests.
    This fixture is automatically applied to all tests.
    """

    print("Setting up environment variables for tests...")
    os.environ["LOG_LEVEL"] = "DEBUG"
