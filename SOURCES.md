# Sources and capture notes

All source URLs below are public. They can change after the snapshot.

| Source | Role | Saved reference |
| --- | --- | --- |
| [Foundation participant API](https://api.solana.org/api/community/v1/sfdp_participants) | Approved cohort and onboarding field | `data/participants.json` |
| [Foundation API documentation](https://solana.org/delegation-api-docs) | Describes participant statuses and endpoint | Link only |
| [Foundation validator pages](https://solana.org/validators-search) | Individual public mainnet history and balances | Exact per-identity page and API URLs in `data/validator_records.json` |
| [Foundation dashboard](https://solana.org/delegation-dashboard) | Published supported-validator and stake aggregates | `data/dashboard_snapshot.json` |
| [Foundation FAQ](https://solana.org/faq) | Twelve-month clock, outside-stake threshold, matching and residual rules | `data/policy_reference.json` |
| [Foundation criteria](https://solana.org/delegation-criteria) | Conflicting older outside-stake threshold | Noted in `data/policy_reference.json` |
| [Foundation renewal form](https://solanafoundation.typeform.com/to/GnddaMFk) | One application for one additional year; no guarantee | Form metadata and paraphrase in `data/policy_reference.json` |
| [Mainnet RPC](https://api.mainnet-beta.solana.com) | Epoch schedule and block-production times | `data/epoch_reference.json` |
| [getEpochSchedule documentation](https://solana.com/docs/rpc/http/getepochschedule) | RPC field definitions | Link only |
| [getBlockTime documentation](https://solana.com/docs/rpc/http/getblocktime) | Estimated block-production timestamp semantics | Link only |

The main census collection window was approximately **2026-11-07 15:36–15:46 UTC**. Individual selected records retain the local file-write timestamp. The renewal page was checked separately at approximately 15:48 UTC; its form metadata showed an update at 2026-11-06 19:52:37 UTC.

The FAQ clock wording was preserved from the English FAQ translation shipped in the official dashboard's HTML at capture time, using the same Next.js build listed in the dashboard reference. This is disclosed provenance, not a claim that a separate full FAQ HTTP response was archived.

## Secondary reporting, not primary cap evidence

- [SolanaFloor post](https://x.com/SolanaFloor/status/2118794673351164047).
- [Crypto Briefing, 6 November 2026](https://cryptobriefing.com/solana-foundation-validator-delegation-program-rules/).

These reported a cap of 100 supported validators and weekly retirement tranches. The original Foundation announcement was not independently retrieved for this release. Neither report is used to classify the 346 rows or compute 308. The FAQ's separate reference to onboarding 100 testnet validators a week is not evidence for the overall support cap.

## Version limitations

API response headers and ETags were not retained. The original broad API response is not distributed because it included unrelated records; only the Approved cohort is published. Complete individual responses are also not distributed because they included fields irrelevant to this research. Every selected source value and the full available mainnet epoch-status mapping for each of the 346 identities are retained in the public inputs and were checked against the original saved responses during audit.
