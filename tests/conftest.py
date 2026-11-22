import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app.db as dbmod
import pytest
from app import create_app


@pytest.fixture(autouse=True)
def reset_mem():
    global dbmod
    dbmod._MEM_CONN = None
    yield
    dbmod._MEM_CONN = None


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as c:
        yield c