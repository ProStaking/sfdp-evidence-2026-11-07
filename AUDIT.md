# Independent verification

## Result: PASS, with interpretation limits

An independent implementation reproduces **346 unique Approved validator identities**, **302 age-screened**, **24 stake-screened**, **18 in both**, and **308 in the union**. The disjoint categories are **284 age-only, 18 both, 6 stake-only, 37 known neither, and 1 unknown**. These are exposure screens, not a confirmed retirement list.

Run from this package's root:

```sh
python scripts/independent_verify.py
```

The verifier uses only the four clean JSON inputs `participants.json`, `validator_records.json`, `analysis_parameters.json`, and `epoch_reference.json` in `data/`. It uses Python's standard library, makes no network requests, and writes no files. It independently calculates counts with integer lamports; it does not import the main recomputation script or trust its output. Failures raise an error and produce a nonzero exit status.

## Checks performed

- Every one of the 346 participant and detail records was inspected, including stale and empty histories. Both identity sets match exactly, with no duplicates, missing identities, extra identities, or state discrepancies.
- Participant records have exactly three allowed fields: validator identity, Approved state, and onboarding epoch. Detail records contain those fields plus public display name, mainnet epoch statuses, the two source stake amounts, source API/page URLs, and local capture time. No extra detail fields passed the allowlist.
- Separately, before packaging, all 346 cleaned participant and detail records were compared against the saved original responses. Every selected source field matched exactly, including complete saved mainnet history dictionaries and original integer lamport strings. No unneeded original fields were copied into this package for this audit.
- The per-record timestamps match local file modification times to millisecond rounding. They are local capture proxies, not server-issued source timestamps.
- The independent script verifies the strict `> 300,000 SOL` stake test using integer subtraction. It verifies the calendar-year cutoff and brackets it between epoch 876's saved block time, November 7, 2025 at 03:25:28 UTC, and epoch 877's, November 9 at 03:27:46 UTC.
- Validator identity public keys are public identifiers, not private credentials. Counting identities does not establish the number of distinct operators or legal entities.

## Coverage and quality findings

- **335** records report positive Foundation stake; **336** show Bonus/Baseline status at epoch 1078. These differ from the **346 Approved** cohort and must not be silently substituted for one another. The dashboard's aggregate count is a separately reported population, not this independently matched identity census.
- **Five** histories do not end at epoch 1078: one ends at 1050, two at 1067, one at 1077, and one is empty. The verifier prints the corresponding public identities. The empty-history record also lacks calculated stake and remains explicitly unknown.
- **241** histories have **3,553 missing epoch keys** between their earliest and latest observed epochs. These are missing entries, not explicit `None` or `NoneHighThirdPartyStake` statuses. **44** histories begin at epoch 196. Complete lifetime eligibility cannot be assumed.
- **19** records have onboarding at or before epoch 876 but first observed Bonus/Baseline eligibility later than 876. Onboarding is not substituted for first eligibility. It may reflect different program semantics or incomplete histories.

## What the result does and does not establish

The public policy clock is the first epoch of eligibility for a Foundation mainnet delegation, **not the age of a stake account**. A recorded old Bonus/Baseline entry supports an old observed eligibility date even when later history contains gaps. Missing earlier entries can make the first *observed* eligibility later than the true first eligibility. Therefore the 37 known-neither records are not proved exempt from the policy; they simply meet neither observable screen in this snapshot.

The snapshot is non-atomic and includes cached API results. Most mainnet histories end at epoch 1078 although the separately recorded chain snapshot was at epoch 1080. Calculated stake fields do not include their own explicit measurement epoch or server timestamp. Subtracting reported Foundation stake from reported activated stake is a transparent proxy, not an independently rebuilt stake-account census or a guarantee of the Foundation's internal enforcement calculation.

The arithmetic does not establish implementation dates, transition treatment, renewal outcomes, individual retirement decisions, or later stake changes. **308 must not be described as 308 confirmed retirements, as a live stake count, or as an unconditional lower bound on real-world retirements.** Source fidelity checks establish that the clean extract faithfully preserves the selected saved fields; they do not authenticate the original remote server responses independently.

This audit covers the census inputs and independent verifier. It is not a separate verification of every policy announcement, secondary source, or later publication artifact. No publication was performed as part of this audit.
