"""Local, deterministic analysis tool. No external requests or AI integration."""
import csv, json, sqlite3, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from planner import ROOT, DB, RADII, covers, load_data, evaluate, optimize

CACHE={}
def solve(radius):
    if radius not in CACHE:
        s,z=load_data();CACHE[radius]=optimize(s,z,radius)
    return CACHE[radius]

def export_analysis(ids,radius):
    sites,zones=load_data(); summary=evaluate(sites,zones,ids,radius)
    if radius not in RADII or not summary['feasible']: raise ValueError('Invalid radius or infeasible selection')
    selected=[s for s in sites if s['site_id'] in ids]
    coverage=[dict(z,covered=int(any(covers(s,z,radius) for s in selected)),
                   covering_sites=';'.join(s['site_id'] for s in selected if covers(s,z,radius))) for z in zones]
    sensitivity=[evaluate(sites,zones,ids,r) for r in RADII]
    outputs=ROOT/'outputs';outputs.mkdir(exist_ok=True)
    def write(name,rows,headers):
        with (outputs/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader();writer.writerows(rows)
    write('selected_sites.csv',selected,['site_id','x_m','y_m','cost_eur'])
    write('zone_coverage.csv',coverage,['zone_id','x_m','y_m','priority_population','covered','covering_sites'])
    ranked=[dict(site_ids=';'.join(r['site_ids']),site_count=r['site_count'],cost_eur=r['cost_eur'],covered_population=r['covered_population'],covered_zone_count=r['covered_zone_count'],radius_m=radius) for r in solve(radius)['ranked']]
    write('feasible_combinations.csv',ranked,list(ranked[0]))
    write('fixed_deployment_sensitivity.csv',[{k:r[k] for k in ('radius_m','covered_population','coverage_pct','covered_zone_count','cost_eur')} for r in sensitivity],['radius_m','covered_population','coverage_pct','covered_zone_count','cost_eur'])
    optimal=solve(radius)['best']
    record=dict(selection=summary,optimal_at_selected_radius=optimal,selection_matches_optimum=summary==optimal,
                fixed_deployment_sensitivity=sensitivity,budget_eur=1000,max_sites=4,
                evaluated_subsets=solve(radius)['evaluated_subsets'],feasible_subsets=solve(radius)['feasible_subsets'])
    (outputs/'analysis_summary.json').write_text(json.dumps(record,indent=2)+'\n')
    with sqlite3.connect(DB) as con:
        con.execute('PRAGMA foreign_keys=ON')
        con.execute('DELETE FROM selected_sites');con.execute('DELETE FROM zone_coverage');con.execute('DELETE FROM analysis_settings')
        con.executemany('INSERT INTO selected_sites VALUES(:site_id,:x_m,:y_m,:cost_eur)',selected)
        con.executemany('INSERT INTO zone_coverage VALUES(:zone_id,:x_m,:y_m,:priority_population,:covered,:covering_sites)',coverage)
        con.executemany('INSERT INTO analysis_settings VALUES(?,?)',[('radius_m',str(radius)),('budget_eur','1000'),('max_sites','4')])
    return dict(saved_to=str(outputs),files=sorted(p.name for p in outputs.glob('*') if p.is_file()),summary=record)

class Handler(BaseHTTPRequestHandler):
    def reply(self,obj,status=200):
        b=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        path=urlparse(self.path);q=parse_qs(path.query)
        try:
            if path.path=='/':
                b=(ROOT/'web'/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
            elif path.path=='/api/data':
                s,z=load_data();self.reply(dict(sites=s,zones=z,budget_eur=1000,max_sites=4))
            elif path.path=='/api/solve': self.reply(solve(int(q.get('radius',['300'])[0])))
            elif path.path=='/api/evaluate':
                s,z=load_data();ids=[v for v in q.get('ids',[''])[0].split(',') if v];r=int(q.get('radius',['300'])[0])
                if r not in RADII: raise ValueError('Invalid radius')
                self.reply(dict(current=evaluate(s,z,ids,r),sensitivity=[evaluate(s,z,ids,a) for a in RADII]))
            else:self.reply(dict(error='Not found'),404)
        except (ValueError,KeyError) as e:self.reply(dict(error=str(e)),400)
    def do_POST(self):
        try:
            if self.path!='/api/export': self.reply(dict(error='Not found'),404);return
            length=int(self.headers.get('Content-Length','0'))
            if length>10000:raise ValueError('Request too large')
            obj=json.loads(self.rfile.read(length));self.reply(export_analysis(obj['ids'],int(obj['radius'])))
        except (ValueError,KeyError,TypeError) as e:self.reply(dict(error=str(e)),400)

if __name__=='__main__':
    if not DB.exists():
        raise SystemExit('Run prepare_data.py once before starting the dashboard.')
    print('Heat Sensor Planner: http://127.0.0.1:8765\nOpen this address in Firefox. Stop using VS Code stop button.')
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
