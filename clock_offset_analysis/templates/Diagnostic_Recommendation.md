# Temperature-sensor clock-offset diagnostic

Status: unfinished. Complete during recording and save as `outputs/Diagnostic_Recommendation.md`.

## Decision
- Selected correction to sensor B timestamps: [complete]
- Sign convention: corrected B timestamp = original B timestamp + selected offset.
- Proposed action (supported correction / further investigation / reject): [complete]
- Evidence supporting this action: [complete]

## Source checks
- Raw reading counts and time coverage: [complete]
- Sampling interval, missing samples and duplicate checks: [complete]
- Common reference-pair counts and window separation: [complete]

## Estimation evidence
- Leading offset and Pearson correlation: [complete]
- Competing offset and correlation: [complete]
- Descriptive correlation gap, not a confidence interval: [complete]
- Why this choice was made before revealing validation: [complete]

## Fixed-offset validation
| Window | Pairs | Original correlation | Aligned correlation | Original MAE °C | Aligned MAE °C | MAE reduction |
|---|---:|---:|---:|---:|---:|---:|
| Estimation | [complete] | [complete] | [complete] | [complete] | [complete] | [complete] |
| Validation | [complete] | [complete] | [complete] | [complete] | [complete] | [complete] |

Remaining mean signed temperature difference, B minus A: [complete].

## Independent verification
- Estimation-only SQL search and squared-correlation comparison: [complete]
- Raw-source reconstruction of original/aligned metrics: [complete]
- Concrete timestamp sign examples: [complete]
- Cross-window and altered-field checks: [complete]
- Original sensor records and temperatures preserved: [complete]

## Limits and follow-up
A stable offset supports a timing explanation, but does not establish clock configuration as the cause. Sensor response lag can also produce timing differences. Alignment does not calibrate either sensor, certify temperature accuracy or establish cold-storage safety. Synthetic data and finite resolution limit generalization.

- Residual disagreement and next investigation: [complete]
- Operational checks before changing real timestamps: [complete]
- Final artifacts inspected: [complete]
