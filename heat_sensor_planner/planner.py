"""Exact coverage optimization. Integer metre coordinates; inclusive radius boundary."""
from itertools import combinations
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'heat_planning.db'
BUDGET = 1000
MAX_SITES = 4
RADII = (200, 300, 400)

def load_data(path=DB):
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        sites = [dict(r) for r in conn.execute('SELECT * FROM candidate_sites ORDER BY site_id')]
        zones = [dict(r) for r in conn.execute('SELECT * FROM demand_zones ORDER BY zone_id')]
    return sites, zones

def covers(site, zone, radius):
    return (site['x_m']-zone['x_m'])**2 + (site['y_m']-zone['y_m'])**2 <= radius**2

def evaluate(sites, zones, ids, radius):
    chosen = [s for s in sites if s['site_id'] in ids]
    if len(chosen) != len(ids) or len(set(ids)) != len(ids):
        raise ValueError('Unknown or repeated site identifier')
    cost = sum(s['cost_eur'] for s in chosen)
    covered = [z for z in zones if any(covers(s,z,radius) for s in chosen)]
    population = sum(z['priority_population'] for z in covered)
    total = sum(z['priority_population'] for z in zones)
    return dict(site_ids=sorted(ids), site_count=len(ids), cost_eur=cost,
                covered_population=population, total_population=total,
                coverage_pct=round(100*population/total,2) if total else 0,
                covered_zone_count=len(covered), zone_count=len(zones), radius_m=radius,
                feasible=len(ids)<=MAX_SITES and cost<=BUDGET)

def rank_key(row):
    return (-row['covered_population'], row['cost_eur'], row['site_count'], tuple(row['site_ids']))

def optimize(sites, zones, radius=300):
    if radius not in RADII:
        raise ValueError('Use a planning radius of 200, 300 or 400 metres')
    # Every subset, including the empty deployment, is evaluated. No heuristic pruning.
    results=[]
    evaluated=0
    for size in range(min(MAX_SITES,len(sites))+1):
        for subset in combinations(sites,size):
            evaluated+=1
            row=evaluate(sites,zones,[s['site_id'] for s in subset],radius)
            if row['feasible']:
                results.append(row)
    results.sort(key=rank_key)
    return dict(best=results[0], ranked=results, evaluated_subsets=evaluated,
                feasible_subsets=len(results), radius_m=radius)
