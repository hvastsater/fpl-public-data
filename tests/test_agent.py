import datetime as dt
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('agent', Path(__file__).parents[1] / 'scripts/agent.py')
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class AgentTests(unittest.TestCase):
    def test_dst(self):
        from zoneinfo import ZoneInfo
        zone = ZoneInfo('Europe/Stockholm')
        self.assertEqual(agent.parse_time('2026-10-23T17:30:00Z').astimezone(zone).hour, 19)
        self.assertEqual(agent.parse_time('2026-10-31T11:00:00Z').astimezone(zone).hour, 12)

    def test_mixed_snapshot(self):
        now = agent.parse_time('2026-10-20T06:33:00Z')
        data = {'generated_at_utc': now.isoformat(), 'events': [{'id':7,'deadline_time':'2026-10-17T10:00:00Z'}], 'entry_picks': {'6':{}}, 'rivals':[{'picks_gw':6}]}
        errors = agent.audit(data, now)['errors']
        self.assertIn('latest_locked_picks_missing_or_inconsistent', errors)
        self.assertIn('rival_picks_missing_or_mixed_gameweek', errors)

    def test_unfinalized_gw(self):
        self.assertEqual(agent.evaluate({'events':[{'id':7,'finished':True,'data_checked':False}]}, {'gameweek':7})['status'], 'waiting_for_official_finalization')

    def test_hits_and_missing_counterfactual(self):
        data = {'events':[{'id':7,'finished':True,'data_checked':True}], 'entry_picks':{'7':{'entry_history':{'event':7,'points':60,'event_transfers_cost':4},'picks':[]}}, 'live_points_gw':7,'live_points':{}}
        result = agent.evaluate(data, {'gameweek':7,'alternatives':[{'id':'roll'}]})
        self.assertEqual(result['actual']['net_points'],56)
        self.assertIsNone(result['alternatives'][0]['realized_net_points'])

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'decision.json'
            agent.save_new(path, {'recommendation':'ROLL'})
            with self.assertRaises(FileExistsError):
                agent.save_new(path, {})


if __name__ == '__main__':
    unittest.main()
