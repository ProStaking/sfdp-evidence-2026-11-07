import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('recompute', ROOT / 'scripts/recompute.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = m.load(ROOT / 'data/analysis_parameters.json')

def fixture(epoch=876, outside=300_000_000_000_000, status='Bonus'):
    return {'validator_identity': 'public-test-identity', 'public_display_name': 'Test',
            'state': 'Approved', 'sfdp2_onboarding_epoch': 577,
            'mainnet_epoch_statuses': {str(epoch): status},
            'activated_stake_last_epoch_lamports': str(outside + 10_000_000_000),
            'foundation_stake_last_epoch_lamports': '10000000000',
            'source_page_url': 'https://example.invalid',
            'source_api_url': 'https://example.invalid',
            'retrieved_at_utc': '2026-11-07T15:40:00Z'}

class RecomputeTests(unittest.TestCase):
    def test_exact_threshold_does_not_trigger_stake(self):
        r = m.classify(fixture(), P)
        self.assertFalse(r['stake_screen_observed'])
        self.assertEqual(r['screen_category'], 'age_only')

    def test_one_lamport_above_threshold_triggers(self):
        self.assertTrue(m.classify(fixture(outside=300_000_000_000_001), P)['stake_screen_observed'])

    def test_epoch_after_anniversary_not_old(self):
        self.assertFalse(m.classify(fixture(epoch=877), P)['age_screen_observed'])

    def test_none_status_does_not_prove_eligibility(self):
        r = m.classify(fixture(status='None'), P)
        self.assertIsNone(r['earliest_observed_eligible_mainnet_epoch'])
        self.assertEqual(r['screen_category'], 'unknown')

    def test_onboarding_age_is_not_used(self):
        r = m.classify(fixture(epoch=1078), P)
        self.assertFalse(r['age_screen_observed'])

    def test_missing_data_is_unknown(self):
        f = fixture()
        f['mainnet_epoch_statuses'] = {}
        f['activated_stake_last_epoch_lamports'] = None
        f['foundation_stake_last_epoch_lamports'] = None
        self.assertEqual(m.classify(f, P)['screen_category'], 'unknown')

    def test_negative_stake_rejected(self):
        with self.assertRaises(ValueError):
            m.classify(fixture(outside=-1), P)

    def test_count_and_overlap_identity(self):
        rows, s = m.reproduce()
        a = s['approved_membership_cohort']
        self.assertEqual(len(rows), 346)
        self.assertEqual(a['either_screen_count'], a['age_screen_count'] + a['stake_screen_count'] - a['overlap_count'])
        self.assertEqual(a['either_screen_count'], 308)
        self.assertEqual(sum(a['categories'].values()), 346)
        self.assertEqual(a['categories']['unknown'], 1)

if __name__ == '__main__':
    unittest.main()
