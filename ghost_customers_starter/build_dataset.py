"""Generate fictional engagement events. Run only for pre-recording setup if needed."""
from pathlib import Path
import sqlite3
import random
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'engagement.db'
SEED = 20261010

def main():
    rng = random.Random(SEED)
    DB.parent.mkdir(exist_ok=True)
    if DB.exists(): DB.unlink()
    cn = sqlite3.connect(DB)
    cn.executescript('''
    CREATE TABLE accounts (
      account_id TEXT PRIMARY KEY, plan TEXT NOT NULL,
      joined_on TEXT NOT NULL
    );
    CREATE TABLE events (
      event_id INTEGER PRIMARY KEY, account_id TEXT NOT NULL,
      session_id TEXT NOT NULL, event_ts TEXT NOT NULL,
      event_type TEXT NOT NULL, page TEXT NOT NULL,
      FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    );
    CREATE INDEX idx_events_session_time ON events(session_id,event_ts);
    CREATE INDEX idx_events_account ON events(account_id);
    ''')
    pages = ['home','search','product','account','help','checkout']
    types = ['page_view','click','scroll','search','add_to_cart']
    rows=[]; accounts=[]; eid=0
    origin=datetime(2026,9,1,8,tzinfo=timezone.utc)
    # Labels are used internally for synthetic construction only, never stored in the database.
    n_sessions=640
    for i in range(n_sessions):
        aid=f'ACC-{i+1:04d}'
        sid=f'SES-{i+1:04d}'
        accounts.append((aid,rng.choice(['basic','plus','premium']),'2026-08-20'))
        mode='regular'
        if i%19==0: mode='metronome'
        elif i%23==0: mode='burst'
        elif i%29==0: mode='linger'
        elif i%31==0: mode='rapid_search'
        start=origin + timedelta(days=rng.randrange(28), hours=rng.randrange(12), minutes=rng.randrange(60))
        if mode=='regular':
            num=rng.randint(8,64)
            intervals=[max(1,rng.lognormvariate(2.5,0.9)) for _ in range(num-1)]
        elif mode=='metronome':
            num=rng.randint(110,175)
            intervals=[5]* (num-1)
        elif mode=='burst':
            num=rng.randint(165,260)
            intervals=[rng.choice([0,0,0,1,1,2]) for _ in range(num-1)]
        elif mode=='linger':
            num=rng.randint(2,5)
            intervals=[rng.randint(1200,3800) for _ in range(num-1)]
        else:
            num=rng.randint(95,150)
            intervals=[rng.choice([1,2,3]) for _ in range(num-1)]
        offset=0
        for j in range(num):
            if j: offset+=intervals[j-1]
            eid+=1
            event_type = ('search' if mode=='rapid_search' else rng.choices(types,weights=[5,4,3,2,1])[0])
            page = ('search' if mode=='rapid_search' else rng.choice(pages))
            dt=start + timedelta(seconds=offset)
            rows.append((eid,aid,sid,dt.isoformat(timespec='seconds'),event_type,page))
    cn.executemany('INSERT INTO accounts VALUES (?,?,?)',accounts)
    cn.executemany('INSERT INTO events VALUES (?,?,?,?,?,?)',rows)
    cn.commit()
    print(f'Prepared synthetic database: {DB}')
    print(f'Accounts/sessions: {len(accounts)} | Events: {len(rows)}')
    cn.close()

if __name__=='__main__': main()
