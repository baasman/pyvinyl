import pytest

from app import create_app, mongo

@pytest.fixture
def app():
    return create_app('testing')

@pytest.fixture
def mongodb():
    return mongo