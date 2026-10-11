"""Create wholly fictional local support records. Run during pre-recording setup."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "support.db"
with sqlite3.connect(DB_PATH) as db:
    db.executescript("""
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS agents;
    CREATE TABLE agents (
      id TEXT PRIMARY KEY,
      display_name TEXT NOT NULL,
      token TEXT NOT NULL UNIQUE
    );
    CREATE TABLE customers (
      id TEXT PRIMARY KEY,
      full_name TEXT NOT NULL,
      segment TEXT NOT NULL,
      owner_agent_id TEXT NOT NULL REFERENCES agents(id),
      case_summary TEXT NOT NULL
    );
    """)
    db.executemany("INSERT INTO agents VALUES (?, ?, ?)", [
       ("AG-001", "Alex Example", "demo-token-alex"),
       ("AG-002", "Morgan Example", "demo-token-morgan"),
    ])
    db.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", [
       ("CUST-101", "Taylor Sample", "consumer", "AG-001", "Fictional plan inquiry"),
       ("CUST-102", "Jordan Sample", "business", "AG-001", "Fictional invoice follow-up"),
       ("CUST-201", "Casey Sample", "consumer", "AG-002", "Fictional device support case"),
       ("CUST-202", "Robin Sample", "business", "AG-002", "Fictional account inquiry"),
    ])
print(f"Created synthetic database at {DB_PATH}")
