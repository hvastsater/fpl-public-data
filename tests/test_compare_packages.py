import unittest
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('compare_packages', Path(__file__).parents[1] / 'scripts/compare_packages.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
compare = module.compare

class Tests(unittest.TestCase):
    def base(self):
        return {'squad':[{'id':i,'position':pos,'team':i,'sell_price':50} for i,pos in enumerate(['GK']*2+['DEF']*5+['MID']*5+['FWD']*3)],'bank':2,'free_transfers':2,'rules':{'hit_cost':4,'max_per_club':3},'packages':[]}
    def package(self,buy=52):
        return {'id':'test','transfers':[{'out':7,'in':{'id':20,'position':'MID','team':20,'buy_price':buy}}],'gross_xp_gain':None}
    def test_exact_budget_and_unknown_forecast(self):
        d=self.base();d['packages']=[self.package()]
        r=compare(d)[1];self.assertTrue(r['feasible']);self.assertEqual(r['bank_after'],0);self.assertIsNone(r['net_xp_gain_vs_roll'])
    def test_over_budget(self):
        d=self.base();d['packages']=[self.package(53)]
        self.assertIn('unaffordable',compare(d)[1]['errors'])
    def test_hit_subtracted(self):
        d=self.base();d['free_transfers']=0;p=self.package();p.update(gross_xp_gain=3,model='test fixture only');d['packages']=[p]
        self.assertEqual(compare(d)[1]['net_xp_gain_vs_roll'],-1)
    def test_duplicate_incoming(self):
        d=self.base();p=self.package();p['transfers'].append({'out':8,'in':p['transfers'][0]['in']});d['packages']=[p]
        self.assertFalse(compare(d)[1]['feasible'])
    def test_missing_sell_price(self):
        d=self.base();del d['squad'][7]['sell_price'];d['packages']=[self.package()]
        self.assertFalse(compare(d)[1]['feasible'])

if __name__=='__main__': unittest.main()
