"""Create fictional inputs only. Does not run optimization or produce recommendations."""
import argparse, csv, json, random, sqlite3
from planner import ROOT, DB

def prepare(path=DB):
    path=__import__('pathlib').Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    rng=random.Random(20261011)
    points=[(100,100),(500,100),(900,100),(1100,300),(100,500),(500,500),
            (900,500),(1100,700),(100,900),(500,900),(900,900),(1100,1100)]
    costs=[180,260,220,310,240,350,270,210,190,280,230,300]
    sites=[(f'S{i+1:02}',x,y,costs[i]) for i,(x,y) in enumerate(points)]
    zones=[]
    for row in range(6):
        for col in range(6):
            x,y=100+col*200,100+row*200
            pop=rng.randint(25,110)+(100 if col>=4 and row>=3 else 0)+(70 if col<=1 and row<=1 else 0)
            zones.append((f'Z{len(zones)+1:02}',x,y,pop))
    with sqlite3.connect(path) as con:
        con.executescript('''
CREATE TABLE candidate_sites(site_id TEXT PRIMARY KEY,x_m INTEGER NOT NULL,y_m INTEGER NOT NULL,cost_eur INTEGER NOT NULL CHECK(cost_eur>0));
CREATE TABLE demand_zones(zone_id TEXT PRIMARY KEY,x_m INTEGER NOT NULL,y_m INTEGER NOT NULL,priority_population INTEGER NOT NULL CHECK(priority_population>=0));
CREATE TABLE selected_sites(site_id TEXT PRIMARY KEY REFERENCES candidate_sites(site_id),x_m INTEGER NOT NULL,y_m INTEGER NOT NULL,cost_eur INTEGER NOT NULL);
CREATE TABLE zone_coverage(zone_id TEXT PRIMARY KEY REFERENCES demand_zones(zone_id),x_m INTEGER NOT NULL,y_m INTEGER NOT NULL,priority_population INTEGER NOT NULL,covered INTEGER NOT NULL CHECK(covered IN(0,1)),covering_sites TEXT NOT NULL);
CREATE TABLE analysis_settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
''')
        con.executemany('INSERT INTO candidate_sites VALUES(?,?,?,?)',sites)
        con.executemany('INSERT INTO demand_zones VALUES(?,?,?,?)',zones)
    return sites,zones

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--reset',action='store_true'); args=parser.parse_args()
    if DB.exists():
        if not args.reset:
            print('Database already exists; preserved. Use --reset only before recording to clear analysis.'); raise SystemExit(0)
        DB.unlink()
        for p in (ROOT/'outputs').glob('*'):
            if p.is_file() and p.name!='.gitkeep': p.unlink()
    sites,zones=prepare()
    for name,headers,rows in [('candidate_sites',('site_id','x_m','y_m','cost_eur'),sites),('demand_zones',('zone_id','x_m','y_m','priority_population'),zones)]:
        with (ROOT/'data'/f'{name}.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(headers);w.writerows(rows)
    print(f'Prepared fictional input database: {DB}\n12 candidate sites; 36 demand zones; analysis tables empty.')
