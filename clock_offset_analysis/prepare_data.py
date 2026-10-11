"""Creates synthetic source inputs and empty output tables; performs no analysis."""
import csv,math,random,sqlite3,argparse
from datetime import datetime,timedelta,timezone
from pathlib import Path
from analysis import ROOT,DB
BASE=datetime(2026,1,15,8,0,0,tzinfo=timezone.utc)
def timestamp(seconds):return (BASE+timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')
def signal(t):
    waves=.32*math.sin(t/180)+.16*math.sin(t/57)+.08*math.sin(t/33)
    pulses=sum(height*math.exp(-.5*((t-center)/width)**2) for center,width,height in [(1800,120,.8),(5100,150,-.65),(9200,100,.75),(12300,130,.85)])
    return 4.2+waves+pulses

def prepare(path=DB):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);rng=random.Random(261011)
    rows=[]
    # Fictional measurements: both raw timestamp grids cover the same four hours.
    # These preparation parameters must not be treated as analyst findings.
    for sensor in ['A','B']:
        for t in range(0,14400,30):
            physical=t if sensor=='A' else t-180
            temp=signal(physical)+(0 if sensor=='A' else .12)+rng.gauss(0,.02 if sensor=='A' else .025)
            rows.append((sensor,t,timestamp(t),round(temp,5)))
    with sqlite3.connect(path) as con:
        con.executescript('''
CREATE TABLE readings(sensor_id TEXT NOT NULL CHECK(sensor_id IN ('A','B')),t_seconds INTEGER NOT NULL,recorded_at TEXT NOT NULL,temperature_c REAL NOT NULL,PRIMARY KEY(sensor_id,t_seconds),UNIQUE(sensor_id,recorded_at));
CREATE TABLE candidate_scores(offset_seconds INTEGER PRIMARY KEY,pair_count INTEGER NOT NULL,correlation REAL,correlation_squared REAL,mae_c REAL NOT NULL,bias_c REAL NOT NULL);
CREATE TABLE phase_metrics(phase TEXT PRIMARY KEY,offset_seconds INTEGER NOT NULL,pair_count INTEGER NOT NULL,baseline_correlation REAL,aligned_correlation REAL,baseline_mae_c REAL NOT NULL,aligned_mae_c REAL NOT NULL,baseline_bias_c REAL NOT NULL,aligned_bias_c REAL NOT NULL,mae_reduction_pct REAL);
CREATE TABLE analysis_settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE aligned_pairs(phase TEXT NOT NULL,reference_t_seconds INTEGER NOT NULL,reference_at TEXT NOT NULL,a_temp_c REAL NOT NULL,b_raw_t_seconds INTEGER NOT NULL,b_original_at TEXT NOT NULL,b_corrected_at TEXT NOT NULL,b_temp_c REAL NOT NULL,baseline_b_temp_c REAL NOT NULL,b_minus_a_c REAL NOT NULL,baseline_b_minus_a_c REAL NOT NULL,PRIMARY KEY(phase,reference_t_seconds));
''')
        con.executemany('INSERT INTO readings VALUES(?,?,?,?)',rows)
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reset',action='store_true');args=p.parse_args()
    if DB.exists():
        if not args.reset:print('Existing database preserved.');raise SystemExit(0)
        DB.unlink()
        for f in (ROOT/'outputs').glob('*'):
            if f.is_file() and f.name!='.gitkeep':f.unlink()
    rows=prepare()
    with (ROOT/'data'/'sensor_readings.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['sensor_id','t_seconds','recorded_at','temperature_c']);w.writerows(rows)
    print(f'Prepared {DB}: 480 readings per sensor, output tables empty.')
