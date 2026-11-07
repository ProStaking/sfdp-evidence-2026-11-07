# SFDP exposure evidence: 7 November 2026

This repository contains the public-data snapshot and reproducible calculations behind ProStaking's [SFDP analysis](https://prostaking.com/blog/sfdp-changes-337-funded-validators-and-the-case-for-planning-ahead/).

**The result is an exposure screen, not a Foundation retirement list or a prediction of validator shutdowns.** Of 346 mainnet identities marked `Approved` in the Foundation participant API, 308 had evidence of at least one of the two conditions screened below. Renewals, transition decisions, missing history, and subsequent changes are not modeled.

## Results

| Observed condition | Approved identities |
| --- | ---: |
| Age condition only | 284 |
| Both age and outside-stake conditions | 18 |
| Outside-stake condition only | 6 |
| Neither condition observed, with data | 37 |
| Insufficient mainnet data | 1 |
| **Total Approved cohort** | **346** |

302 + 24 − 18 = **308**, or **89.0%** of 346.

| Non-SFDP stake | Approved identities |
| --- | ---: |
| Under 50,000 SOL | 96 |
| 50,000 to under 100,000 SOL | 126 |
| 100,000 through 300,000 SOL | 99 |
| More than 300,000 SOL | 24 |
| Unknown | 1 |

These are **Approved memberships**, not 346 simultaneously funded validators. At collection, the [official dashboard](https://solana.org/delegation-dashboard) separately displayed **337 validators receiving Foundation stake**, **23.75 million SOL**, 60 locations, and 26 countries, for epoch 1078. Individual records contained 335 positive Foundation balances; 299 of those records met at least one screen. These cohorts must not be substituted for one another.

## Files to inspect

- [Per-validator CSV](data/validator_exposure.csv): all 346 identities, public display names, source links, balances, history boundaries, and classifications.
- [Selected source records](data/validator_records.json): the public mainnet epoch histories and integer balance fields used to derive every row.
- [Approved participant cohort](data/participants.json): the cohort selected from the official participant API.
- [Methodology and limitations](METHODOLOGY.md).
- [Machine-readable summary](data/summary.json).
- [Primary derivation](scripts/recompute.py), [independent verification](scripts/independent_verify.py), and [audit findings](AUDIT.md).
- [Source and timing references](SOURCES.md), [policy reference](data/policy_reference.json), and [epoch/RPC reference](data/epoch_reference.json).
- `SHA256SUMS`: checksums for the reviewed release files. Checksums verify consistency, not independent authenticity of the original server responses.

## Reproduce offline

Python 3.10 or later is sufficient. No dependencies, credentials, network calls, or API keys are needed.

```sh
python3 scripts/recompute.py --check
python3 scripts/independent_verify.py
python3 -m unittest discover -s tests -v
```

The first command checks every CSV row and all saved summary counts. To write fresh outputs without changing the published evidence:

```sh
python3 scripts/recompute.py --output /tmp/sfdp-recomputed
```

On macOS, verify the release files with `shasum -a 256 -c SHA256SUMS`; on Linux use `sha256sum -c SHA256SUMS`. Python may generate local `__pycache__` files; those are not evidence files or part of the manifest.

## What this package does not establish

The policy clock is first mainnet eligibility, **not stake-account age, validator-key creation, or the SFDP onboarding field**. We use observed eligible history as evidence, not as proof that the history is complete. A recent earliest observation does not prove the validator is younger than one year.

The 100-supported-validator cap and weekly retirement tranches were reported by SolanaFloor and Crypto Briefing. The original Foundation announcement was not independently retrieved for this package. The cap is not part of the 308 calculation. Comparing the dashboard's 337 supported validators with 100 slots gives 237 fewer slots, not 237 proven shutdowns. Comparing 346 Approved records with 100 support slots uses a different denominator and does not establish that 246 memberships will be revoked.

All account addresses in this repository are **public validator identity keys**, included for verification. No private keys, credentials, account-holder contact details, application responses, KYC status, private conversations, or unrelated operator records are included. Only the 346-row cohort and public data needed to reproduce the analysis are distributed.
