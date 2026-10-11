# Recording and narration — exact pointers and expected results

Practice guide only; keep it off-screen during recording. These expected numbers come from the unchanged synthetic starter. Confirm observed results before saying them. If a value differs, investigate rather than reading a prepared conclusion. No final diagnostic memo has been completed for you.

Target about 20–25 minutes, subject to genuine work. Do not pad time. Narrate any keyboard shortcuts before/while using them; toolbar actions are available for executing SQL. Point to the named result or control while explaining what, where and why.

## 1. Opening — under 20 seconds
Show the exact approved Goal in your approved opening app (Goal.html in Firefox if permitted). Say:

> I will be beginning my task soon. Here is the workflow I have in mind.

Move to DBeaver.

## 2. DBeaver input audit — approximately 0:20–5:00
Point to sensors.db and investigations.sql:

> I am investigating whether a consistent timing displacement explains disagreement between two fictional colocated temperature sensors. Sensor A is the reference clock in this scenario. I will choose a correction using the first three hours, then assess it unchanged on the final hour.

Run ONE numbered query at a time.

### 01 — source counts
Point to A: 480, B: 480.

> There are four hundred and eighty readings from each sensor, giving nine hundred and sixty source records in total.

### 02 — duplicate raw timestamps
Point to the empty result grid.

> This checks timestamp uniqueness within each sensor. No duplicate timestamps were found.

### 03 — required fields and identifiers
Point to the conditions and empty grid.

> Both sensor identifiers are valid, and the required timestamp and temperature fields are present. No invalid rows were returned.

### 04 — numerical/grid validity
Point to t_seconds modulo 30 and the empty grid.

> The relative times are integers on the thirty-second grid and lie within the four-hour recording range. Temperature values are numeric. This query found no violations.

### 05 — timestamp conversion
Point to the UTC start timestamp in the query and empty results.

> I am checking that each UTC timestamp agrees with its relative time from eight o'clock. The two time representations are consistent.

### 06 — sampling gaps
Point to LAG and the empty result.

> Consecutive readings should be thirty seconds apart. No gaps or irregular intervals were found in either sensor.

### 07 — coverage and temperature ranges
Point to 08:00:00 and 11:59:30 for both sensors.

> Both raw series run from eight o'clock through eleven fifty-nine thirty UTC. They cover the same four-hour timestamp grid.

Point to A range 3.44743–5.09213 and B range 3.57544–5.26642.

> Sensor A ranges from approximately three point four four seven to five point zero nine two degrees Celsius. Sensor B ranges from three point five seven five to five point two six six. Those ranges describe the observations; they do not certify accuracy or storage safety.

### 08 — raw timestamps missing from the other sensor
Point to the empty result.

> Every raw timestamp has a reading from both sensors. There are no unmatched raw timestamps.

### 09 — raw-window counts
Point to estimation: 360 for each sensor, validation: 120 for each.

> The first three hours contain three hundred and sixty readings per sensor. The separate final hour contains one hundred and twenty per sensor. I will not use the final-hour results to choose the offset.

### 10 — common reference-pair counts
Point to estimation 320, validation 80.

> To compare offsets fairly, the tool trims ten minutes from both ends of each reference window. That leaves three hundred and twenty estimation pairs and eighty validation pairs. Every candidate uses the same reference timestamps within its phase.

### 11 — integrity
Point to ok.

> The SQLite integrity check reports okay. I will now inspect the estimation series in Firefox.

## 3. Firefox estimation — approximately 5:00–12:00

### Original series and sign
Point to Estimation · original timestamps and its blue/orange legend.

> The blue trace is sensor A and the orange trace is sensor B at the original timestamps. The temperature changes are visibly out of step. I will test a range of timestamp corrections rather than infer an offset from one peak.

Point to Estimation metrics, Original column:

> On the common estimation grid, the original Pearson correlation is zero point three eight five two one six. Mean absolute disagreement is zero point three zero six four five three degrees Celsius.

Point to Sign convention and pairing; expand it.

> The correction is added to B's original timestamp. A negative correction moves B earlier. For a reference time t, the tool pairs A at t with B recorded at t minus the correction. Temperature measurements themselves are not changed.

### Candidate comparison
Point to Compare offsets — estimation only; click.

> I will compare forty-one candidate corrections, from minus ten to plus ten minutes in thirty-second increments. This search uses only the estimation window.

Point to the candidate-count line and Pairs column:

> All forty-one candidates use three hundred and twenty identical reference times, so differing sample counts do not explain the ranking.

Point to rank 1:

> The leading correction is minus one hundred and eighty seconds. Its correlation is zero point nine nine four eight one two, with mean absolute error of zero point one two two zero five seven degrees Celsius.

Point to rank 2, then rank 3:

> The next candidates are minus one hundred and fifty seconds, with correlation zero point nine five six five six one, and minus two hundred and ten seconds, with correlation zero point nine five six two one five.

Click rank 2 to inspect its plot, then point to the Offset profile:

> The neighboring offset produces visibly less alignment and a lower correlation. The profile has its strongest peak at minus one hundred and eighty seconds. The gap from the runner-up is zero point zero three eight two five two. This is a descriptive comparison, not a confidence interval.

### Select and inspect the estimation leader
Click Select estimation leader. Point to Proposed timestamp correction: -180 s.

> Based on estimation evidence, I am selecting a minus-three-minute correction to B's timestamps.

Point to the before/after plots and Estimation metrics:

> The aligned shapes are much closer. Correlation rises from zero point three eight five two one six to zero point nine nine four eight one two. Mean absolute error falls from zero point three zero six four five three to zero point one two two zero five seven degrees Celsius, a sixty point one seven percent reduction.

Point to Mean signed error, Aligned: +0.122057.

> A positive temperature difference remains: B is approximately zero point one two two degrees warmer on average in the paired readings. Timing alignment does not remove this bias and should not be described as calibration.

### Concrete sign example
Point to Pairing audit: A 09:00:00, original B 09:03:00, corrected B 09:00:00.

> For this example, A's nine o'clock reading is paired with B's original nine-oh-three reading. Subtracting one hundred and eighty seconds places that B timestamp at nine o'clock. The original B time and temperature are preserved.

## 4. Firefox fixed-offset validation — approximately 12:00–15:00

Point to Freeze offset and validate.

> I have chosen the correction from estimation evidence. I will now freeze it before revealing the separate final-hour results. I will not retune it based on validation.

Click. Point to the frozen-offset notice and disabled selector.

> The correction is locked at minus one hundred and eighty seconds.

Point to validation Pair count: 80.

> Validation uses eighty common-interior reference pairs from the final raw-time hour. Both the original and aligned comparisons use the same reference times.

Point to validation correlations:

> Correlation increases from zero point two zero seven eight eight eight at the original timestamps to zero point nine nine four seven seven nine after the fixed correction.

Point to validation MAEs and reduction:

> Mean absolute error falls from zero point three one six two five six to zero point one one eight eight zero four degrees Celsius. That is a sixty-two point four three percent reduction.

Point to aligned signed error +0.118804:

> A residual positive difference of approximately zero point one one nine degrees remains. The timing correction improves agreement in both windows, while the remaining temperature bias needs separate investigation.

Point to validation pairing-audit row A 11:20, original B 11:23, corrected B 11:20:

> The same sign convention holds in validation: B's eleven twenty-three timestamp moves to eleven twenty. This is the unchanged correction selected earlier.

Point to Save analysis files; click.

> I am saving candidate scores, phase metrics, aligned comparison pairs, the proposed corrected B series and the analysis summary. Saving also populates SQLite analysis tables for independent verification. It does not overwrite raw sensor readings.

## 5. DBeaver independent verification — approximately 15:00–20:00
Refresh/reconnect the same sensors.db connection. Run queries 12–24.

### 12 — readiness
Point to READY.

> The saved analysis is ready: forty-one candidate scores, four hundred paired rows and two phase-metric rows are present, and the fixed offset has been validated.

### 13 — settings
Point to offset_seconds -180 and validated 1.

> The saved correction is minus one hundred and eighty seconds. The validated flag confirms that the final-hour assessment was performed.

### 14 — candidate pair equality
Point to candidates 41, min_pairs 320, max_pairs 320.

> Every candidate used exactly three hundred and twenty estimation pairs. The saved search preserves equal pairing opportunity.

### 15 — stored rankings
Point to the first row -180, then -150 and -210.

> The saved leading and competing candidates match those reviewed in Firefox.

### 16 — independent estimation-only search
Point to raw readings joins, then the top row -180, signed_correlation_squared 0.989652, MAE 0.122057.

> This SQL reconstructs candidate pairings independently from the raw readings. It also ranks minus one hundred and eighty seconds first. The signed correlation-squared value is zero point nine eight nine six five two and the mean absolute error is zero point one two two zero five seven.

> This query reports squared correlation to avoid depending on a SQLite square-root extension. I compare it with the dashboard's correlation-squared row, not directly with its Pearson correlation.

### 17 — original readings and correction sign
Point to the empty result.

> No inconsistencies were found between the exported pairs and raw source readings. Original B temperatures and timestamps agree, and adding the saved correction maps B to the reference time.

### 18 — window separation
Point to the empty result.

> No pair crosses from one raw-time phase into another. Estimation and validation remain separate.

### 19 — concrete timestamp examples
Point to the two rows:
- Estimation: A 09:00, original B 09:03, corrected B 09:00; A 4.62260°C, B 4.71295°C.
- Validation: A 11:20, original B 11:23, corrected B 11:20; A 3.97601°C, B 4.07813°C.

> These two independently inspected examples confirm the minus-three-minute timestamp correction in both phases. The temperatures remain their original measured values; they have not been forced to match.

### 20 — independent raw-source metrics
Point to estimation/aligned: 320 pairs, MAE 0.122057, bias 0.122057, correlation_squared 0.989652.

> The raw-source reconstruction confirms the aligned estimation metrics: three hundred and twenty pairs, mean absolute error zero point one two two zero five seven, and squared correlation zero point nine eight nine six five two.

Point to validation/aligned: 80 pairs, MAE/bias 0.118804, correlation_squared 0.989585.

> The fixed-offset validation reconstruction confirms eighty pairs, mean absolute error zero point one one eight eight zero four and squared correlation zero point nine eight nine five eight five. These agree with the dashboard.

Point to baseline rows if explaining the original comparison:
- Estimation: MAE 0.306453, bias 0.126581, r² 0.148391.
- Validation: MAE 0.316256, bias 0.093921, r² 0.043217.

> The independently reconstructed original-timestamp errors also agree with the before-alignment results.

### 21 — saved phase metrics
Point to the same offset -180 in both rows, MAE reductions 60.17 and 62.43.

> Both phases use the same correction. The saved mean-absolute-error reductions are sixty point one seven percent for estimation and sixty-two point four three percent for validation.

### 22 — exported pair metrics
Point to 320 estimation / 80 validation and corresponding MAEs.

> The paired export has the expected three hundred and twenty estimation and eighty validation rows. Its temperature-difference metrics agree with the independent source reconstruction.

### 23 — altered baseline/difference fields
Point to the empty result.

> No altered baseline temperatures or inconsistent difference fields were found.

### 24 — remaining raw counts
Point to 480 for A and B.

> Both sensors still have all four hundred and eighty original readings. The tool preserved the raw input table while storing the analysis separately.

## 6. VS Code artifacts and recommendation — approximately 20:00–25:00

Open outputs/candidate_offsets.csv. Point to leading and competing rows.

> This export preserves all forty-one estimation candidates, rather than only the ten shown on screen.

Open outputs/phase_metrics.csv. Point to the two phases and their common offset.

> These rows preserve the before-and-after metrics for the unchanged correction across estimation and validation.

Open outputs/aligned_pairs.csv. Find the 09:00 or 11:20 example.

> The pair export retains the reference time, original B time, proposed corrected time and original measured temperatures. This makes the correction auditable.

Open outputs/corrected_sensor_b.csv. Point to its first row: original 08:00, corrected 07:57.

> The full corrected series preserves every original B observation. Its first proposed timestamp is seven fifty-seven because the correction moves the original eight o'clock reading earlier by three minutes. These boundary observations are retained rather than discarded.

Point to the final row: original 11:59:30, corrected 11:56:30.

> The same correction is applied consistently through the last observation. This export contains four hundred and eighty B readings, whereas the paired comparison uses four hundred common-interior pairs across both phases.

Open outputs/analysis_summary.json. Point to selected_offset_seconds, selection_matches_estimation_leader, and phases.

> The summary records the selected correction, its agreement with the estimation leader, and both phase assessments. It contains computed evidence; I will now document the diagnostic judgment.

Open templates/Diagnostic_Recommendation.md. Complete it using the observed values, then save as outputs/Diagnostic_Recommendation.md. Do not leave any [complete] placeholders or the unfinished status.

While writing, explain:

> The results support a consistent temporal alignment proposal: move B's recorded timestamps earlier by three minutes relative to A. The correlation and error improvement persist in the separate final-hour assessment.

> This does not establish that the clock itself is the cause. Sensor response lag can also produce temporal displacement. A positive temperature bias remains after alignment, so I recommend checking timestamp acquisition and clock configuration separately from calibration or placement differences.

> I would retain original records, verify the time configuration and sensor response behavior, and assess additional periods before applying a real operational correction. This analysis does not establish cold-storage safety.

Open the completed memo's Markdown preview and point to the metrics, verification and limitations.

> I am checking that the decision, sign convention, unchanged validation offset, residual bias and limitations are complete and consistent with the verified exports.

## Closing
With the completed recommendation visible:

> The diagnostic recommendation and supporting artifacts are saved. The minus-three-minute correction was selected from estimation evidence, assessed unchanged in validation and independently verified in SQL. The memo separates improved timing agreement from residual temperature bias and documents the required operational follow-up.

Stop TaskRecorder and wait for archiving. Run the packaging configuration only after recording ends.

## Result reference table — unchanged starter
| Metric | Estimation original | Estimation aligned | Validation original | Validation aligned |
|---|---:|---:|---:|---:|
| Pairs | 320 | 320 | 80 | 80 |
| Pearson correlation | 0.385216 | 0.994812 | 0.207888 | 0.994779 |
| Correlation squared | 0.148391 | 0.989652 | 0.043217 | 0.989585 |
| MAE °C | 0.306453 | 0.122057 | 0.316256 | 0.118804 |
| Mean signed difference B−A °C | 0.126581 | 0.122057 | 0.093921 | 0.118804 |
| MAE reduction | — | 60.17% | — | 62.43% |

Leading correction: -180 s; runner-up -150 s; descriptive correlation gap 0.038252. These expected values are preparation guidance, not a completed client report.
