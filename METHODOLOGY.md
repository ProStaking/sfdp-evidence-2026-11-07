# Methodology and limitations

## 1. Freeze the cohort

The source is the Foundation's documented [participant endpoint](https://api.solana.org/api/community/v1/sfdp_participants), described in its [API documentation](https://solana.org/delegation-api-docs). Select records whose `state` is exactly `Approved`, and count distinct `mainnetBetaPubkey` values. This produced 346 unique identities. Pending, TestnetOnboarded, Rejected, and Retired records are not in the published cohort.

`data/participants.json` contains the selected public identity, status, and onboarding epoch. `data/validator_records.json` contains the matching selected fields from each public detail endpoint used by the Foundation's validator pages. This second endpoint is part of the website's implementation, rather than the documented participant API; its schema may change.

The complete detail responses contained other fields that are unnecessary for this analysis. Those fields were excluded, not published. The selected fields preserve source values; amounts remain decimal strings of integer lamports.

## 2. Calculate outside stake with integer arithmetic

For each identity:

```
non-SFDP stake = activated_stake_last_epoch − foundation_stake_last_epoch
```

Both fields come from `mnCalculatedStats` in the same detail response. The stake condition is strictly **greater than 300,000 SOL**, or **greater than 300,000,000,000,000 lamports**. Exactly 300,000 SOL does not trigger it. One SOL is 1,000,000,000 lamports.

No floating-point comparison is used. Self-stake, stake-pool stake, and other non-Foundation stake all remain included; this is not a measure of unique delegators or independently attracted community stake. The source field is a cached last-epoch measure, not a live balance at publication time.

## 3. Establish observed old eligibility

Read `mnStats.epochs` and select epochs whose status is `Baseline` or `Bonus`. The earliest such epoch is called **earliest observed eligible mainnet epoch**. `None`, `NoneHighThirdPartyStake`, and absent epoch keys are not treated as eligibility evidence.

The [Foundation FAQ](https://solana.org/faq) measures its twelve-month term from first mainnet eligibility. The snapshot reference time is approximately 7 November 2026 at 15:46 UTC, making the anniversary 7 November 2025 at 15:46 UTC. Mainnet `getEpochSchedule` reported 432,000 slots per epoch. `getBlockTime` for slot 378,432,000 returned 1762485928, corresponding to **epoch 876 beginning 7 November 2025 at 03:25:28 UTC**. Epoch 877 began 9 November 2025. Thus observed eligibility at epoch 876 or earlier passes the age screen.

These are estimated on-chain block-production times, not administrative determinations about when a particular membership began. There is no observed first eligible epoch at 874, 875, or 876 in this cohort, so moving this boundary back to 875 does not change the result. Do not substitute a fixed number of epochs for twelve calendar months: epoch duration changed during the period.

The onboarding field is published for comparison but is **not used** for the age flag. Using onboarding alone would flag 321 identities rather than 302; 19 older onboarding records have a more recent first visible eligible epoch. We do not infer why these records differ.

## 4. Combine the conditions without double counting

The union is `age flag OR stake flag`. The intersection is `age flag AND stake flag`. Therefore:

- Age observed: 302.
- Outside stake above threshold: 24.
- Both observed: 18.
- Either observed: 302 + 24 − 18 = **308**.
- Categories: 284 age only, 18 both, 6 stake only, 37 neither observed with data, 1 unknown.

“Neither observed” is not a guarantee of continued eligibility. The unknown record has no public mainnet history or stake fields in this snapshot and is not silently counted as a clean result.

## 5. Distinguish membership, eligibility, and balances

The dashboard's 337 supported validators, the 346 Approved identity records, the 336 records with `Baseline` or `Bonus` at epoch 1078, and the 335 positive Foundation balances are different measurements. Public aggregates, eligibility assessments, balances, and participant status are cached and can update on different schedules. The analysis is not an atomic ledger snapshot, and the dashboard number is not replaced with a hand-constructed count.

Five Approved records have no epoch-1078 history: two histories end at 1067, one at 1077, one at 1050, and one is empty. Nine of the 308 flagged Approved records have no positive Foundation balance. Calling all 308 currently funded validators that will newly lose support would be incorrect.

## 6. Limits of the history and policy inference

An audit found 241 histories with internal missing epoch keys, totaling 3,553 absent entries between each history's first and last stored key. These are absent keys, not explicit non-eligible statuses. Missing data cannot erase an old eligible epoch that was observed, but it can hide earlier eligibility. Identity changes, program migrations, incomplete retention, administrative exceptions, and renewals are not resolved by this dataset. Forty-four histories begin at epoch 196; that is an observation about retained data, not proof that those validators first joined then.

The screen does not apply renewal decisions, reconstruct complete operator tenure across identities, forecast the selection order, or determine which validators will shut down. The 308 count is reproducible evidence of potential exposure under the stated conditions, **not a confirmed retirement count or an unconditional lower bound on actual retirements**.

The FAQ stated a 300,000-SOL threshold, while the criteria page still displayed 1,000,000 SOL when checked. The renewal form allowed one application for one additional year and said approval was not guaranteed. The original Foundation announcement establishing the reported 100-validator cap and weekly tranches was not independently retrieved. These uncertainties are disclosed rather than resolved by assumption.

## 7. Snapshot timing and integrity

The participant response was locally saved at approximately 15:36:09 UTC, the dashboard at 15:36:29, and individual detail records between 15:37:58 and 15:46:15, all on 7 November 2026. File-write times are approximate local capture times, not authenticated server-issued timestamps. The dashboard carried Next.js build `V-kMocdNxGt4Ar01a7SbX`; no API ETags, HTTP Last-Modified values, server version identifiers, or signed responses were retained.

The included JSON is the frozen selected-field evidence used for this result. Live endpoint requests now may return different values and do not recreate this historical capture. The offline scripts reproduce the calculation from the frozen inputs; they do not independently authenticate those inputs. `SHA256SUMS` makes subsequent file changes detectable against the reviewed release. See the repository commit for the exact published version.
