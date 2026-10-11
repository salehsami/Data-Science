"""Deterministic paired-series analysis. No AI service or third-party dependencies."""
from pathlib import Path
from statistics import mean
from math import sqrt
import sqlite3
ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'sensors.db'
STEP=30
MAX_OFFSET=600
OFFSETS=tuple(range(-MAX_OFFSET,MAX_OFFSET+1,STEP))
WINDOWS={'estimation':(0,10800),'validation':(10800,14400)}

def load_readings(path=DB):
    with sqlite3.connect(path) as con:
        con.row_factory=sqlite3.Row
        rows=[dict(r) for r in con.execute('SELECT * FROM readings ORDER BY sensor_id,t_seconds')]
    out={'A':{},'B':{}}
    for row in rows:
        if row['sensor_id'] not in out:raise ValueError('Unexpected sensor identifier')
        if row['t_seconds'] in out[row['sensor_id']]:raise ValueError('Duplicate sensor timestamp')
        if row['temperature_c'] is None:raise ValueError('Missing temperature')
        out[row['sensor_id']][row['t_seconds']]=row
    if any(not values for values in out.values()):raise ValueError('Both sensors require readings')
    return out

def common_reference_times(data,phase):
    """Same A timestamps for every offset, restricted to one raw-time window."""
    lo,hi=WINDOWS[phase]
    eligible=[]
    for t in sorted(data['A']):
        if not lo+MAX_OFFSET<=t<hi-MAX_OFFSET:continue
        if all(lo<=t-offset<hi and t-offset in data['B'] for offset in OFFSETS):eligible.append(t)
    if len(eligible)<3:raise ValueError('Insufficient common pairs for this window')
    return eligible

def pairs(data,phase,offset):
    if offset not in OFFSETS:raise ValueError('Offset must be -600 to +600 seconds in 30-second increments')
    return [(data['A'][t],data['B'][t-offset],data['B'][t]) for t in common_reference_times(data,phase)]

def metrics(pair_rows,offset):
    a=[r[0]['temperature_c'] for r in pair_rows];b=[r[1]['temperature_c'] for r in pair_rows]
    am,bm=mean(a),mean(b)
    numerator=sum((x-am)*(y-bm) for x,y in zip(a,b))
    aa=sum((x-am)**2 for x in a);bb=sum((y-bm)**2 for y in b)
    corr=numerator/sqrt(aa*bb) if aa>0 and bb>0 else None
    return {'offset_seconds':offset,'pair_count':len(a),'correlation':corr,
            'correlation_squared':corr*corr if corr is not None else None,
            'mae_c':mean(abs(y-x) for x,y in zip(a,b)),
            'bias_c':mean(y-x for x,y in zip(a,b))}

def rank_key(row):
    return (-(row['correlation'] if row['correlation'] is not None else -2),row['mae_c'],abs(row['offset_seconds']),row['offset_seconds'])

def estimate(data):
    rows=[metrics(pairs(data,'estimation',offset),offset) for offset in OFFSETS]
    if any(row['correlation'] is None for row in rows):raise ValueError('Correlation is undefined for a constant series')
    rows.sort(key=rank_key)
    return {'candidates':rows,'best':rows[0],'runner_up':rows[1],
            'correlation_gap':rows[0]['correlation']-rows[1]['correlation'],
            'candidate_count':len(rows),'phase':'estimation'}

def assess(data,phase,offset):
    baseline=metrics(pairs(data,phase,0),0);aligned=metrics(pairs(data,phase,offset),offset)
    reduction=100*(baseline['mae_c']-aligned['mae_c'])/baseline['mae_c'] if baseline['mae_c'] else None
    return {'phase':phase,'baseline':baseline,'aligned':aligned,'mae_reduction_pct':reduction}

def plot_rows(data,phase,offset):
    return [{'t_seconds':a['t_seconds'],'time':a['recorded_at'],'a_c':a['temperature_c'],
             'baseline_b_c':original['temperature_c'],'aligned_b_c':b['temperature_c'],
             'b_raw_t_seconds':b['t_seconds']} for a,b,original in pairs(data,phase,offset)]
