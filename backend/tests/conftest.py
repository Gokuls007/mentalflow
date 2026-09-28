import os
import sys
import tempfile

import pytest

# Use an isolated SQLite database and model directory for the test run
_tmpdir = tempfile.mkdtemp(prefix="mentalflow-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmpdir, 'test.db')}"
os.environ.pop("GROQ_API_KEY", None)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _isolated_cwd():
    # RL model files (models/*.pkl) are written relative to the working directory
    old = os.getcwd()
    os.chdir(_tmpdir)
    yield
    os.chdir(old)


@pytest.fixture(scope="session")
def client():
    # TrustedHostMiddleware only accepts localhost / 127.0.0.1 / *.mentalflow.ai
    with TestClient(app, base_url="http://localhost") as c:
        yield c


@pytest.fixture(scope="session")
def auth_headers(client):
    creds = {"email": "demo.patient@example.com", "password": "password123"}
    r = client.post("/api/v1/users/register", json=creds)
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/users/login", json=creds)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
