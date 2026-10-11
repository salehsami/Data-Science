import json,csv,sqlite3
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from analysis import ROOT,DB,OFFSETS,load_readings,estimate,assess,plot_rows,pairs
from prepare_data import timestamp

VALIDATED=None

def export(offset):
    if VALIDATED!=offset:raise ValueError('Validate the fixed offset before exporting')
    data=load_readings();est=estimate(data)
    phases=[assess(data,p,offset) for p in ['estimation','validation']]
    aligned=[]
    for p in ['estimation','validation']:
        for a,b,base in pairs(data,p,offset):
            aligned.append({'phase':p,'reference_t_seconds':a['t_seconds'],'reference_at':a['recorded_at'],
                            'a_temp_c':a['temperature_c'],'b_raw_t_seconds':b['t_seconds'],'b_original_at':b['recorded_at'],
                            'b_corrected_at':timestamp(b['t_seconds']+offset),'b_temp_c':b['temperature_c'],
                            'baseline_b_temp_c':base['temperature_c'],'b_minus_a_c':b['temperature_c']-a['temperature_c'],
                            'baseline_b_minus_a_c':base['temperature_c']-a['temperature_c']})
    corrected=[dict(sensor_id='B',original_t_seconds=t,original_timestamp=row['recorded_at'],
                    corrected_t_seconds=t+offset,corrected_timestamp=timestamp(t+offset),
                    temperature_c=row['temperature_c'],offset_seconds=offset)
               for t,row in sorted(data['B'].items())]
    phase_rows=[]
    for r in phases:
        b,a=r['baseline'],r['aligned'];phase_rows.append(dict(phase=r['phase'],offset_seconds=offset,pair_count=a['pair_count'],baseline_correlation=b['correlation'],aligned_correlation=a['correlation'],baseline_mae_c=b['mae_c'],aligned_mae_c=a['mae_c'],baseline_bias_c=b['bias_c'],aligned_bias_c=a['bias_c'],mae_reduction_pct=r['mae_reduction_pct']))
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    def write(name,rows):
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write('candidate_offsets.csv',est['candidates']);write('phase_metrics.csv',phase_rows)
    write('aligned_pairs.csv',aligned);write('corrected_sensor_b.csv',corrected)
    summary={'selected_offset_seconds':offset,'sign_convention':'corrected B timestamp = original B timestamp + offset',
             'best_estimation_offset_seconds':est['best']['offset_seconds'],
             'estimation_correlation_gap':est['correlation_gap'],'candidate_count':est['candidate_count'],
             'selection_matches_estimation_leader':offset==est['best']['offset_seconds'],
             'phases':phases,'source_readings_unchanged':True,
             'correction_scope':'timestamp proposal only; temperatures unchanged; not a calibration or safety conclusion'}
    (out/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with sqlite3.connect(DB) as con:
        for table in ['candidate_scores','phase_metrics','aligned_pairs','analysis_settings']:con.execute('DELETE FROM '+table)
        con.executemany('INSERT INTO candidate_scores VALUES(:offset_seconds,:pair_count,:correlation,:correlation_squared,:mae_c,:bias_c)',est['candidates'])
        con.executemany('INSERT INTO phase_metrics VALUES(:phase,:offset_seconds,:pair_count,:baseline_correlation,:aligned_correlation,:baseline_mae_c,:aligned_mae_c,:baseline_bias_c,:aligned_bias_c,:mae_reduction_pct)',phase_rows)
        con.executemany('INSERT INTO aligned_pairs VALUES(:phase,:reference_t_seconds,:reference_at,:a_temp_c,:b_raw_t_seconds,:b_original_at,:b_corrected_at,:b_temp_c,:baseline_b_temp_c,:b_minus_a_c,:baseline_b_minus_a_c)',aligned)
        con.executemany('INSERT INTO analysis_settings VALUES(?,?)',[('offset_seconds',str(offset)),('validated','1'),('step_seconds','30'),('max_offset_seconds','600')])
    return {'files':[p.name for p in sorted(out.glob('*')) if p.is_file() and p.name!='.gitkeep'],'saved_to':str(out)}

class Handler(BaseHTTPRequestHandler):
    def reply(self,obj,status=200):
        b=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        path=urlparse(self.path);q=parse_qs(path.query)
        try:
            if path.path=='/':
                b=(ROOT/'web'/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
            data=load_readings()
            if path.path=='/api/initial':
                self.reply({'raw_counts':{s:len(data[s]) for s in ['A','B']},'baseline':assess(data,'estimation',0),'plot':plot_rows(data,'estimation',0),'offsets':OFFSETS})
            elif path.path=='/api/estimate':self.reply(estimate(data))
            elif path.path=='/api/preview':
                offset=int(q.get('offset',['0'])[0]);self.reply({'metrics':assess(data,'estimation',offset),'plot':plot_rows(data,'estimation',offset)})
            else:self.reply({'error':'Not found'},404)
        except (ValueError,KeyError,TypeError) as e:self.reply({'error':str(e)},400)
    def do_POST(self):
        global VALIDATED
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>10000:raise ValueError('Request too large')
            obj=json.loads(self.rfile.read(n));offset=int(obj['offset'])
            if offset not in OFFSETS:raise ValueError('Invalid offset')
            if self.path=='/api/validate':
                if VALIDATED is not None and VALIDATED!=offset:raise ValueError('Validation offset is frozen; restart only before a new analysis')
                data=load_readings();VALIDATED=offset
                self.reply({'metrics':assess(data,'validation',offset),'plot':plot_rows(data,'validation',offset),'locked_offset_seconds':offset})
            elif self.path=='/api/export':self.reply(export(offset))
            else:self.reply({'error':'Not found'},404)
        except (ValueError,KeyError,TypeError) as e:self.reply({'error':str(e)},400)
if __name__=='__main__':
    if not DB.exists():raise SystemExit('Prepare inputs before starting the tool.')
    print('Clock Offset Analysis: http://127.0.0.1:8766\nOpen in Firefox. Stop using the VS Code stop button.')
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
