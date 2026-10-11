# Method and code explanation

## Offset sign
The offset is a correction applied to B's recorded timestamps, not a shift to its measured temperature. If the proposed correction is negative, B moves earlier. To pair reference time t, look up B at t minus offset. For example a -180 second correction maps an original B time of 09:03 to a corrected time of 09:00.

This is not conclusive evidence that the clock is wrong: sensor response differences or other delays can mimic temporal displacement. The memo must distinguish shape agreement from verified clock configuration.

## Equal pairing opportunity
`common_reference_times()` trims the maximum permitted shift (600 seconds) from both ends of each reference window. It also requires all tested offsets to have available B samples within that same raw-time phase. Thus `pairs()` uses identical A times for every candidate, even when a missing B reading forces common times to be removed.

The bundled complete dataset yields A reference times 08:10:00–10:49:30 for estimation (320 pairs), and 11:10:00–11:49:30 for validation (80 pairs). The remaining raw samples are retained; trimming affects only comparison pairs.

## Metrics
Pearson correlation is centered covariance divided by the product of centered standard-deviation terms. It measures shape agreement and is unchanged by a constant temperature bias. Mean absolute error averages |B-A|. Mean signed error averages B-A. A positive signed error means B is warmer in the paired readings.

These metrics answer different questions. A near-one correlation can coexist with persistent measurement disagreement. Improvement after alignment supports the proposed timing explanation but does not remove calibration uncertainty.

## Estimation and validation
`estimate()` evaluates 41 candidates using estimation only. It does not inspect validation. `assess()` applies one fixed offset to a specified phase. The server exposes validation only when Freeze offset and validate is clicked and then locks the choice for the session. Restart only for a new analysis; do not retune based on the final hour.

## SQL independence
Query 16 reconstructs all candidate pairs from raw inputs, computes aggregate covariance terms and ranks **signed correlation squared**. This signed-square transform is monotonic on [-1,1] and ranks negative correlations correctly. Query 20 reconstructs original and aligned phase pairs directly from raw readings and saved offset, then computes MAE, bias and correlation squared.

Squared correlation is used because a DBeaver SQLite driver need not include the SQRT extension. Compare these values with the dashboard's Correlation squared row, not its Pearson correlation row. Numeric rounding is for display only; ranking in Python uses unrounded values.

## Exports
Saving writes CSVs/JSON and analysis tables in SQLite. The source `readings` table is never modified by the application. `corrected_sensor_b.csv` retains 480 original B readings with proposed timestamps and unchanged temperatures. `aligned_pairs.csv` contains only the 400 common-interior comparison pairs across both windows.

The application computes evidence, not a final client decision. Complete the diagnostic memo yourself during recording.
