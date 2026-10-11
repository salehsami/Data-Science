import sys,unittest,tempfile,sqlite3,threading,json,urllib.request,csv,zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import *
from prepare_data import prepare
import server,package_deliverables

class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.db=self.root/'data'/'sensors.db';prepare(self.db);self.data=load_readings(self.db)
    def tearDown(self):self.temp.cleanup()
    def test_inputs_and_no_outputs(self):
        self.assertEqual([len(self.data[s]) for s in ['A','B']],[480,480])
        with sqlite3.connect(self.db) as c:
            for t in ['candidate_scores','phase_metrics','aligned_pairs','analysis_settings']:self.assertEqual(c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0],0)
    def test_recovered_shift(self):
        e=estimate(self.data);self.assertEqual(e['best']['offset_seconds'],-180);self.assertEqual(e['candidate_count'],41);self.assertGreater(e['correlation_gap'],.03)
    def test_same_counts_and_no_cross_window(self):
        for phase,count in [('estimation',320),('validation',80)]:
            lo,hi=WINDOWS[phase]
            for o in OFFSETS:
                p=pairs(self.data,phase,o);self.assertEqual(len(p),count)
                self.assertTrue(all(lo<=a['t_seconds']<hi and lo<=b['t_seconds']<hi for a,b,base in p))
    def test_missing_sample_keeps_common_reference_set(self):
        del self.data['B'][3000]
        counts=[len(pairs(self.data,'estimation',o)) for o in OFFSETS]
        self.assertEqual(len(set(counts)),1);self.assertLess(counts[0],320)
    def test_validation_fixed_shift_and_remaining_bias(self):
        e=estimate(self.data);r=assess(self.data,'validation',e['best']['offset_seconds'])
        self.assertGreater(r['aligned']['correlation'],.99);self.assertGreater(r['mae_reduction_pct'],60)
        self.assertGreater(r['aligned']['bias_c'],.1)
    def test_sign_convention(self):
        a,b,base=next(row for row in pairs(self.data,'estimation',-180) if row[0]['t_seconds']==3600)
        self.assertEqual(b['t_seconds'],3780);self.assertEqual(b['t_seconds']-180,a['t_seconds'])
    def test_invalid_offset(self):
        with self.assertRaises(ValueError):pairs(self.data,'estimation',17)
    def test_independent_sql_search(self):
        statements=sql_statements()
        with sqlite3.connect(self.db) as c:rows=c.execute(statements[15]).fetchall()
        best=estimate(self.data)['best'];self.assertEqual(rows[0][0],best['offset_seconds']);self.assertAlmostEqual(rows[0][2],round(best['correlation_squared'],6),places=6)
    def test_http_export_and_independent_metrics(self):
        import shutil
        for folder in ['web','sql','templates','tests','.vscode']:
            shutil.copytree(ROOT/folder,self.root/folder,ignore=shutil.ignore_patterns('__pycache__'))
        for name in ['analysis.py','server.py','prepare_data.py','package_deliverables.py','README.md']:
            (self.root/name).write_text((ROOT/name).read_text() if (ROOT/name).exists() else 'QA fixture')
        (self.root/'docs').mkdir();(self.root/'docs'/'INPUT_BRIEF.md').write_text('QA fixture')
        (self.root/'data'/'sensor_readings.csv').write_text('QA fixture')
        with patch.object(server,'ROOT',self.root),patch.object(server,'DB',self.db),patch.object(server,'load_readings',lambda: self.data),patch.object(server,'VALIDATED',None):
            httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=httpd.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(httpd.server_port)
            def post(path,offset):
                req=urllib.request.Request(base+path,data=json.dumps({'offset':offset}).encode(),headers={'Content-Type':'application/json'},method='POST');return json.load(urllib.request.urlopen(req))
            try:
                with self.assertRaises(urllib.error.HTTPError):post('/api/export',-180)
                initial=json.load(urllib.request.urlopen(base+'/api/initial'));self.assertNotIn('validation',initial)
                self.assertIn(b'Clock Offset Analysis',urllib.request.urlopen(base+'/').read())
                e=json.load(urllib.request.urlopen(base+'/api/estimate'));self.assertEqual(e['best']['offset_seconds'],-180)
                preview=json.load(urllib.request.urlopen(base+'/api/preview?offset=-180'));self.assertEqual(preview['metrics']['phase'],'estimation')
                validated=post('/api/validate',-180);self.assertEqual(validated['metrics']['phase'],'validation')
                with self.assertRaises(urllib.error.HTTPError):post('/api/validate',-150)
                post('/api/export',-180)
                with sqlite3.connect(self.db) as c:
                    allrows=[c.execute(q).fetchall() for q in sql_statements()]
                    self.assertEqual(allrows[11][0][0],'READY')
                    self.assertEqual(allrows[13][0],(41,320,320))
                    for index in [16,17,22]:self.assertEqual(allrows[index],[])
                    for phase,mode,count,mae,bias,corrsq in allrows[19]:
                        expected=assess(self.data,phase,-180)['aligned' if mode=='aligned' else 'baseline']
                        self.assertEqual(count,expected['pair_count']);self.assertAlmostEqual(mae,round(expected['mae_c'],6),places=6);self.assertAlmostEqual(corrsq,round(expected['correlation_squared'],6),places=6)
                with (self.root/'outputs'/'corrected_sensor_b.csv').open() as f:rows=list(csv.DictReader(f))
                self.assertEqual(len(rows),480)
                for row in rows:
                    self.assertEqual(int(row['corrected_t_seconds']),int(row['original_t_seconds'])-180)
                    self.assertEqual(float(row['temperature_c']),self.data['B'][int(row['original_t_seconds'])]['temperature_c'])
                with patch.object(package_deliverables,'ROOT',self.root),patch.object(package_deliverables,'DB',self.db):
                    with self.assertRaises(ValueError):package_deliverables.package()
                    (self.root/'outputs'/'Diagnostic_Recommendation.md').write_text('Completed QA fixture; not a task recommendation.')
                    target=package_deliverables.package()
                    with zipfile.ZipFile(target) as z:self.assertIsNone(z.testzip());self.assertFalse(any('Metadata.rtf' in n for n in z.namelist()))
            finally:httpd.shutdown();httpd.server_close()

def sql_statements():
    statements=[];buffer=''
    for line in (ROOT/'sql'/'investigations.sql').read_text().splitlines(True):
        buffer+=line
        if sqlite3.complete_statement(buffer):statements.append(buffer);buffer=''
    return statements
if __name__=='__main__':unittest.main()
