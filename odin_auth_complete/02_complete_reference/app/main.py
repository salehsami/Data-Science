"""Fictional support API with server-side object-level authorization.

Never use query-string agent IDs as authority. The authenticated agent is
obtained from the bearer token and compared to the database owner.
"""
from contextlib import closing
from pathlib import Path
import sqlite3
from fastapi import FastAPI, Header, HTTPException, status

DB_PATH = Path(__file__).resolve().parents[1] / "support.db"
app = FastAPI(title="Support Records API", version="1.0.0")

def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def authenticate(authorization: str | None) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing bearer token",
                            headers={"WWW-Authenticate": "Bearer"})
    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token.strip():
        raise HTTPException(status_code=401, detail="Invalid authorization header",
                            headers={"WWW-Authenticate": "Bearer"})
    with closing(connect()) as db:
        agent = db.execute(
            "SELECT id, display_name FROM agents WHERE token = ?", (token.strip(),)
        ).fetchone()
    if agent is None:
        raise HTTPException(status_code=401, detail="Invalid bearer token",
                            headers={"WWW-Authenticate": "Bearer"})
    return dict(agent)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/customers/{customer_id}")
def customer_record(customer_id: str, authorization: str | None = Header(default=None)):
    agent = authenticate(authorization)
    with closing(connect()) as db:
        customer = db.execute(
            "SELECT id, full_name, segment, owner_agent_id, case_summary "
            "FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer["owner_agent_id"] != agent["id"]:
        raise HTTPException(status_code=403, detail="Customer access denied")
    return {"requested_by": agent["id"], "customer": dict(customer)}
