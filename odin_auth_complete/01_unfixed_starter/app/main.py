"""Synthetic support customer API — intentionally missing ownership authorization."""
from contextlib import closing
from pathlib import Path
import sqlite3
from fastapi import FastAPI, Header, HTTPException

DB_PATH = Path(__file__).resolve().parents[1] / "support.db"
app = FastAPI(title="Support Records API", version="0.1.0")


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def authenticate(authorization: str | None) -> sqlite3.Row:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization[7:]
    with closing(connect()) as db:
        agent = db.execute("SELECT id, display_name FROM agents WHERE token = ?", (token,)).fetchone()
    if agent is None:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return agent


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers/{customer_id}")
def customer_record(customer_id: str, authorization: str | None = Header(default=None)):
    agent = authenticate(authorization)
    with closing(connect()) as db:
        customer = db.execute(
            "SELECT id, full_name, segment, owner_agent_id, case_summary FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # INTENTIONAL DEFECT: authentication succeeds but customer ownership is not checked.
    # Professional task: determine appropriate authorization policy and implement it.
    return {"requested_by": agent["id"], "customer": dict(customer)}
