import random
import sqlite3
from pathlib import Path
from datetime import datetime,timedelta

ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'deliveries.db'
DB.parent.mkdir(exist_ok=True)
if DB.exists(): DB.unlink()
rng=random.Random(20261010)
conn=sqlite3.connect(DB)
conn.execute('''CREATE TABLE deliveries (delivery_id TEXT PRIMARY KEY, dispatched_at TEXT NOT NULL, algorithm_version TEXT NOT NULL CHECK(algorithm_version IN ('Old','New')), distance_category TEXT NOT NULL CHECK(distance_category IN ('Short','Medium','Long')), distance_km REAL NOT NULL, delivery_minutes INTEGER NOT NULL, promised_minutes INTEGER NOT NULL, on_time INTEGER NOT NULL CHECK(on_time IN (0,1)))''')
# The mix differs strongly between versions. Both algorithms are deliberately better within every distance band for New.
plan={'Old':{'Short':(760,0.94,20),'Medium':(190,0.79,35),'Long':(50,0.52,55)},'New':{'Short':(160,0.97,20),'Medium':(340,0.85,35),'Long':(500,0.63,55)}}
rows=[]; i=0
for version, segments in plan.items():
    for distance,(count,rate,promise) in segments.items():
        flags=[1]*round(count*rate)+[0]*(count-round(count*rate));rng.shuffle(flags)
        for on_time in flags:
            i+=1
            km=round(rng.uniform(*{'Short':(0.8,3.9),'Medium':(4.0,9.9),'Long':(10.0,22.0)}[distance]),1)
            mins=promise-rng.randint(1,8) if on_time else promise+rng.randint(1,14)
            dt=(datetime(2026,8,1)+timedelta(minutes=rng.randint(0,60*24*28))).isoformat(timespec='minutes')
            rows.append((f'DLV-{i:05d}',dt,version,distance,km,mins,promise,on_time))
rng.shuffle(rows)
conn.executemany('INSERT INTO deliveries VALUES (?,?,?,?,?,?,?,?)',rows)
conn.commit();print(f'Prepared synthetic dataset: {DB} ({len(rows)} rows)')
conn.close()
