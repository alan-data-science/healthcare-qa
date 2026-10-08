import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "clinic.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "DATABASE": str(db_path),
        }
    )
    with app.test_client() as client:
        yield client
