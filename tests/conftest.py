import os

import pytest


@pytest.fixture
def headless_backend():
    old_backends = os.environ.get("WLR_BACKENDS", "")
    os.environ["WLR_BACKENDS"] = "headless"
    yield
    os.environ["WLR_BACKENDS"] = old_backends
