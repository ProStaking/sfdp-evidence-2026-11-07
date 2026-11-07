#!/usr/bin/env python3
"""Independently verify the frozen census using only this package's clean JSON.

Uses Python's standard library; makes no network requests and writes no files.
Run: python scripts/independent_verify.py
An optional first argument selects another copy of the package root.
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


participants = load('participants.json')['records']
records = load('validator_records.json')['records']
params = load('analysis_parameters.json')
epochs = load('epoch_reference.json')
participant_fields = {'validator_identity', 'state', 'sfdp2_onboarding_epoch'}
record_fields = participant_fields | {
    'activated_stake_last_epoch_lamports', 'foundation_stake_last_epoch_lamports',
    'mainnet_epoch_statuses', 'public_display_name', 'retrieved_at_utc',
    'source_api_url', 'source_page_url',
}
for row in participants:
    require(set(row) == participant_fields, 'Unexpected participant fields')
for row in records:
    require(set(row) == record_fields, 'Unexpected detail fields')
participant_ids = {r['validator_identity'] for r in participants}
record_ids = {r['validator_identity'] for r in records}
require(len(participants) == len(participant_ids) == 346, 'Participant count or duplicate identity')
require(len(records) == len(record_ids) == 346, 'Detail count or duplicate identity')
require(participant_ids == record_ids, 'Participant and detail identity sets differ')
participant_by_id = {r['validator_identity']: r for r in participants}
require(set(params['eligible_statuses']) == {'Baseline', 'Bonus'}, 'Eligibility statuses changed')
require(params['lamports_per_sol'] == 10**9, 'SOL conversion changed')
require(int(params['stake_threshold_lamports']) == 300000 * 10**9, 'Stake threshold changed')
require(params['last_epoch_start_before_anniversary'] == 876, 'Age cutoff changed')
cutoff = datetime.fromisoformat(params['twelve_calendar_month_cutoff_utc'].replace('Z', '+00:00'))
reference = datetime.fromisoformat(params['age_reference_time_utc'].replace('Z', '+00:00'))
require(reference.replace(year=reference.year - 1) == cutoff, 'Calendar anniversary mismatch')
times = {}
for entry in epochs['block_time_responses']:
    epoch = entry['epoch']
    response = entry['response']
    if 'result' in response:
        require(entry['request']['params'] == [epoch * 432000], 'Unexpected epoch start slot')
        timestamp = datetime.fromtimestamp(response['result'], timezone.utc)
        require(timestamp == datetime.fromisoformat(entry['utc_time'].replace('Z', '+00:00')), 'RPC time rendering mismatch')
        times[epoch] = timestamp
require(times[876] <= cutoff < times[877], 'Cutoff is not bracketed by epochs 876 and 877')
counts = Counter()
quality = Counter()
stale = []
for row in records:
    key = row['validator_identity']
    require(row['state'] == participant_by_id[key]['state'] == 'Approved', 'State mismatch')
    require(row['sfdp2_onboarding_epoch'] == participant_by_id[key]['sfdp2_onboarding_epoch'], 'Onboarding mismatch')
    require(row['source_api_url'] == f'https://api.solana.org/api/validators/{key}?cacheStatus=enable', 'Unexpected API URL')
    require(row['source_page_url'] == f'https://solana.org/sfdp-validators/{key}', 'Unexpected page URL')
    history = row['mainnet_epoch_statuses']
    require(isinstance(history, dict), 'Invalid history')
    require(all(e.isdigit() and s in {'None', 'Bonus', 'Baseline', 'NoneHighThirdPartyStake'} for e, s in history.items()), 'Unexpected history entry')
    eligible = [int(e) for e, status in history.items() if status in {'Baseline', 'Bonus'}]
    first = min(eligible) if eligible else None
    age = first is not None and first <= 876
    amounts = [row[k] for k in ('activated_stake_last_epoch_lamports', 'foundation_stake_last_epoch_lamports')]
    require(all(x is None or (isinstance(x, str) and x.isdigit()) for x in amounts), 'Invalid lamport amount')
    non_sfdp = int(amounts[0]) - int(amounts[1]) if all(x is not None for x in amounts) else None
    require(non_sfdp is None or non_sfdp >= 0, 'Negative non-SFDP stake')
    stake = non_sfdp is not None and non_sfdp > 300000 * 10**9
    unknown = non_sfdp is None or first is None
    counts['approved'] += 1
    counts['age'] += age
    counts['stake'] += stake
    counts['both'] += age and stake
    counts['union'] += age or stake
    counts['age_only'] += age and not stake
    counts['stake_only'] += stake and not age
    counts['unknown'] += unknown
    counts['known_neither'] += not (age or stake or unknown)
    values = set(map(int, history))
    latest = max(values) if values else None
    if latest != 1078:
        stale.append({'validator_identity': key, 'latest_recorded_epoch': latest})
    if values:
        gaps = max(values) - min(values) + 1 - len(values)
        quality['histories_with_internal_missing_epochs'] += gaps > 0
        quality['internal_missing_epochs'] += gaps
        quality['histories_starting_at_epoch_196'] += min(values) == 196
    quality['empty_histories'] += not bool(values)
    quality['eligible_at_1078'] += history.get('1078') in {'Baseline', 'Bonus'}
    quality['positive_foundation_stake'] += amounts[1] is not None and int(amounts[1]) > 0
    quality['onboarding_cutoff_disagreements'] += first is not None and row['sfdp2_onboarding_epoch'] <= 876 < first
expected = {'approved': 346, 'age': 302, 'stake': 24, 'both': 18, 'union': 308,
            'age_only': 284, 'stake_only': 6, 'unknown': 1, 'known_neither': 37}
require(dict(counts) == expected, f'Census mismatch: {dict(counts)}')
expected_quality = {'histories_with_internal_missing_epochs': 241, 'internal_missing_epochs': 3553,
                    'histories_starting_at_epoch_196': 44, 'empty_histories': 1,
                    'eligible_at_1078': 336, 'positive_foundation_stake': 335,
                    'onboarding_cutoff_disagreements': 19}
require(dict(quality) == expected_quality, f'Quality inventory mismatch: {dict(quality)}')
require(len(stale) == 5, 'Unexpected number of stale or empty histories')
print(json.dumps({'result': 'PASS', 'counts': dict(counts), 'data_quality': dict(quality),
                  'stale_or_empty_histories': stale}, indent=2))
