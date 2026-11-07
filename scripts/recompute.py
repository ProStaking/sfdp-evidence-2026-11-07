#!/usr/bin/env python3
"""Recompute the saved SFDP exposure screen offline, using integer lamports."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def sol(lamports: int | None) -> str:
    if lamports is None:
        return ''
    sign = '-' if lamports < 0 else ''
    value = abs(lamports)
    return f'{sign}{value // 1_000_000_000}.{value % 1_000_000_000:09d}'

def classify(record: dict, parameters: dict) -> dict:
    statuses = record['mainnet_epoch_statuses']
    qualifying = sorted(int(epoch) for epoch, status in statuses.items()
                        if status in parameters['eligible_statuses'])
    first = qualifying[0] if qualifying else None
    total_raw = record['activated_stake_last_epoch_lamports']
    foundation_raw = record['foundation_stake_last_epoch_lamports']
    total = int(total_raw) if total_raw is not None else None
    foundation = int(foundation_raw) if foundation_raw is not None else None
    outside = total - foundation if total is not None and foundation is not None else None
    if outside is not None and outside < 0:
        raise ValueError(f"Negative outside stake for {record['validator_identity']}")
    age = first is not None and first <= parameters['last_epoch_start_before_anniversary']
    stake = outside is not None and outside > int(parameters['stake_threshold_lamports'])
    if age and stake:
        category = 'both'
    elif age:
        category = 'age_only'
    elif stake:
        category = 'stake_only'
    elif first is None or outside is None:
        category = 'unknown'
    else:
        category = 'neither_observed'
    if outside is None:
        band = 'unknown'
    elif outside < 50_000 * 1_000_000_000:
        band = 'under_50000'
    elif outside < 100_000 * 1_000_000_000:
        band = '50000_to_under_100000'
    elif outside <= 300_000 * 1_000_000_000:
        band = '100000_to_300000_inclusive'
    else:
        band = 'over_300000'
    return {
        'validator_identity': record['validator_identity'],
        'public_display_name': record['public_display_name'] or '',
        'program_state': record['state'],
        'sfdp2_onboarding_epoch_not_used_for_age_screen': record['sfdp2_onboarding_epoch'],
        'earliest_observed_eligible_mainnet_epoch': first,
        'latest_observed_mainnet_epoch': max(map(int, statuses)) if statuses else None,
        'status_at_epoch_1078': statuses.get(str(parameters['mainnet_history_reference_epoch']), 'missing'),
        'activated_stake_last_epoch_lamports': total,
        'foundation_stake_last_epoch_lamports': foundation,
        'non_sfdp_stake_lamports': outside,
        'non_sfdp_stake_sol': sol(outside),
        'age_screen_observed': age,
        'stake_screen_observed': stake,
        'either_screen_observed': age or stake,
        'screen_category': category,
        'non_sfdp_stake_band': band,
        'source_page_url': record['source_page_url'],
        'source_api_url': record['source_api_url'],
        'approximate_local_saved_at_utc': record['retrieved_at_utc'],
    }

def summarize(rows: list[dict]) -> dict:
    categories = {k: sum(r['screen_category'] == k for r in rows)
                  for k in ('age_only', 'both', 'stake_only', 'neither_observed', 'unknown')}
    bands = {k: sum(r['non_sfdp_stake_band'] == k for r in rows)
             for k in ('under_50000', '50000_to_under_100000',
                       '100000_to_300000_inclusive', 'over_300000', 'unknown')}
    return {
        'count': len(rows),
        'known_stake_records': sum(r['non_sfdp_stake_lamports'] is not None for r in rows),
        'age_screen_count': sum(r['age_screen_observed'] for r in rows),
        'stake_screen_count': sum(r['stake_screen_observed'] for r in rows),
        'overlap_count': categories['both'],
        'either_screen_count': sum(r['either_screen_observed'] for r in rows),
        'categories': categories,
        'non_sfdp_stake_bands': bands,
    }

def reproduce(root: Path = ROOT) -> tuple[list[dict], dict]:
    participants = load(root / 'data/participants.json')['records']
    records = load(root / 'data/validator_records.json')['records']
    parameters = load(root / 'data/analysis_parameters.json')
    identities = [r['validator_identity'] for r in participants]
    record_ids = [r['validator_identity'] for r in records]
    assert len(set(identities)) == len(identities), 'Duplicate participant identity'
    assert len(set(record_ids)) == len(record_ids), 'Duplicate detail identity'
    assert set(identities) == set(record_ids), 'Participant/detail cohort mismatch'
    assert all(r['state'] == 'Approved' for r in participants + records)
    rows = [classify(r, parameters) for r in sorted(records, key=lambda x: x['validator_identity'])]
    funded = [r for r in rows if (r['foundation_stake_last_epoch_lamports'] or 0) > 0]
    summary = {'approved_membership_cohort': summarize(rows),
               'positive_foundation_balance_subset': summarize(funded)}
    return rows, summary

def write_outputs(out: Path, rows: list[dict], summary: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    with (out / 'validator_exposure.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write a fresh CSV and summary to this directory')
    parser.add_argument('--check', action='store_true', help='Compare every CSV row and summary with saved outputs')
    args = parser.parse_args()
    rows, summary = reproduce()
    if args.output:
        write_outputs(args.output, rows, summary)
    if args.check:
        expected = load(ROOT / 'data/summary.json')
        assert summary == expected, 'Summary differs from saved output'
        with (ROOT / 'data/validator_exposure.csv').open(encoding='utf-8', newline='') as handle:
            stored = list(csv.DictReader(handle))
        comparable = [{k: '' if v is None else str(v) for k, v in r.items()} for r in rows]
        assert comparable == stored, 'One or more saved CSV rows differs'
        print(f'PASS: all {len(rows)} rows and every summary count reproduce exactly.')
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
