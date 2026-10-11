import sys, unittest, tempfile, sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from planner import covers,evaluate,optimize,load_data
from prepare_data import prepare

class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'test.db';prepare(self.path);self.s,self.z=load_data(self.path)
    def tearDown(self):self.temp.cleanup()
    def test_input_state(self):
        self.assertEqual((len(self.s),len(self.z)),(12,36))
        with sqlite3.connect(self.path) as con:self.assertEqual(con.execute('SELECT COUNT(*) FROM selected_sites').fetchone()[0],0)
    def test_boundary(self):
        self.assertTrue(covers({'x_m':0,'y_m':0},{'x_m':300,'y_m':400},500))
        self.assertFalse(covers({'x_m':0,'y_m':0},{'x_m':300,'y_m':400},499))
    def test_overlap_counted_once(self):
        sites=[dict(site_id=i,x_m=0,y_m=0,cost_eur=100) for i in ['A','B']]
        zones=[dict(zone_id='Z',x_m=0,y_m=0,priority_population=90)]
        self.assertEqual(evaluate(sites,zones,['A','B'],300)['covered_population'],90)
    def test_constraints_enumeration_and_optimum(self):
        out=optimize(self.s,self.z);self.assertEqual(out['evaluated_subsets'],794)
        self.assertTrue(all(r['feasible'] for r in out['ranked']))
        # Independent bit-mask enumeration and direct set union.
        expected=[]
        for mask in range(1<<len(self.s)):
            subset=[s for i,s in enumerate(self.s) if mask&(1<<i)]
            if len(subset)>4 or sum(s['cost_eur'] for s in subset)>1000:continue
            ids=tuple(s['site_id'] for s in subset)
            covered={z['zone_id'] for z in self.z for s in subset if (s['x_m']-z['x_m'])**2+(s['y_m']-z['y_m'])**2<=90000}
            pop=sum(z['priority_population'] for z in self.z if z['zone_id'] in covered)
            expected.append((-pop,sum(s['cost_eur'] for s in subset),len(subset),ids))
        best=min(expected);actual=out['best'];self.assertEqual(tuple(actual['site_ids']),best[3]);self.assertEqual(actual['covered_population'],-best[0]);self.assertEqual(len(expected),out['feasible_subsets'])
    def test_tie_breaks(self):
        s=[dict(site_id=i,x_m=0,y_m=0,cost_eur=c) for i,c in [('A',200),('B',100),('C',100)]]
        z=[dict(zone_id='Z',x_m=0,y_m=0,priority_population=30)]
        self.assertEqual(optimize(s,z)['best']['site_ids'],['B'])
    def test_sensitivity(self):
        ids=optimize(self.s,self.z)['best']['site_ids'];p=[evaluate(self.s,self.z,ids,r)['covered_population'] for r in [200,300,400]];self.assertEqual(p,sorted(p))
    def test_sql_independent_optimum(self):
        sql=(Path(__file__).resolve().parents[1]/'sql'/'04_independent_optimality.sql').read_text()
        with sqlite3.connect(self.path) as con:rows=con.execute(sql).fetchall()
        best=optimize(self.s,self.z)['best'];self.assertEqual(rows[0],(';'.join(best['site_ids']),best['site_count'],best['cost_eur'],best['covered_population']))
    def test_unknown_and_invalid_radius(self):
        with self.assertRaises(ValueError):evaluate(self.s,self.z,['UNKNOWN'],300)
        with self.assertRaises(ValueError):optimize(self.s,self.z,999)
if __name__=='__main__':unittest.main()
