"""Request-level regression suite; uses a separate temporary SQLite database."""
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app import main

@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_support.db"
    with sqlite3.connect(db_file) as db:
        db.executescript("""
            CREATE TABLE agents (id TEXT PRIMARY KEY, display_name TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE);
            CREATE TABLE customers (id TEXT PRIMARY KEY, full_name TEXT NOT NULL,
                segment TEXT NOT NULL, owner_agent_id TEXT NOT NULL,
                case_summary TEXT NOT NULL);
            INSERT INTO agents VALUES ('AG-001','Alex Example','demo-token-alex');
            INSERT INTO agents VALUES ('AG-002','Morgan Example','demo-token-morgan');
            INSERT INTO customers VALUES
                ('CUST-101','Taylor Sample','consumer','AG-001','Fictional inquiry'),
                ('CUST-201','Casey Sample','consumer','AG-002','Fictional inquiry');
        """)
    monkeypatch.setattr(main, "DB_PATH", db_file)
    with TestClient(main.app) as test_client:
        yield test_client

def bearer(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.parametrize("token,customer,owner", [
    ("demo-token-alex", "CUST-101", "AG-001"),
    ("demo-token-morgan", "CUST-201", "AG-002"),
])
def test_owner_can_access(client, token, customer, owner):
    response = client.get(f"/customers/{customer}", headers=bearer(token))
    assert response.status_code == 200
    assert response.json()["requested_by"] == owner
    assert response.json()["customer"]["owner_agent_id"] == owner

@pytest.mark.parametrize("token,customer", [
    ("demo-token-alex", "CUST-201"),
    ("demo-token-morgan", "CUST-101"),
])
def test_cross_agent_access_denied(client, token, customer):
    response = client.get(f"/customers/{customer}", headers=bearer(token))
    assert response.status_code == 403
    assert "customer" not in response.json()

def test_missing_token(client):
    response = client.get("/customers/CUST-101")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

def test_invalid_token(client):
    assert client.get("/customers/CUST-101", headers=bearer("wrong-token")).status_code == 401

def test_malformed_auth_header(client):
    assert client.get("/customers/CUST-101", headers={"Authorization": "Basic abc"}).status_code == 401

def test_unknown_customer(client):
    assert client.get("/customers/CUST-999", headers=bearer("demo-token-alex")).status_code == 404

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
