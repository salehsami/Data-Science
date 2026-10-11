# Fictional client brief and input provenance

Two colocated cold-storage temperature sensors show disagreement during changes in room temperature. Sensor A is the scenario's reference clock. Assess whether one consistent timestamp adjustment to B improves agreement, and whether evidence holds on a separate final-hour window. A timing explanation does not establish the real-world cause.

## Inputs
- SQLite table `readings`; CSV copy `data/sensor_readings.csv`.
- Columns: `sensor_id`, integer `t_seconds` relative to 2026-01-15 08:00 UTC, original ISO UTC `recorded_at`, `temperature_c`.
- Four hours of raw timestamps from 08:00:00 through 11:59:30 UTC, half-open [08:00,12:00).
- 30-second sampling, 480 records per sensor; 960 total.
- Estimation raw window [08:00,11:00), 360 rows per sensor.
- Validation raw window [11:00,12:00), 120 rows per sensor.

## Predefined methods
Compare offsets from -600 to +600 seconds in 30-second increments. Corrected B timestamp equals original B timestamp plus the selected correction. A negative correction proposes earlier B timestamps. Candidate choice uses estimation data only: highest Pearson correlation, lower MAE, smaller absolute offset, then offset as deterministic tie rules. Correlation gaps are descriptive, not confidence intervals.

For fair comparisons, trim 600 seconds from both ends of each A reference window and use A times for which all candidate B raw times exist within that same phase. For complete inputs: 320 estimation pairs and 80 validation pairs, identical for each candidate. No cross-window pairing, interpolation, temperature calibration or model training is performed.

Freeze the chosen offset before viewing final-hour metrics. Evaluate the unchanged correction in validation; do not retune based on final-hour evidence. Preserve original records and temperatures.

## Provenance and scope
All inputs and application code are AI-generated before recording. `prepare_data.py` uses deterministic synthetic signal generation and seeded measurement noise. No public dataset, copyright-dependent assets, personal information, external maps or accounts are required. Preparation code contains simulation parameters; these are not substitutes for observed analytical evidence and should not be used to bypass the diagnostic work.

A proposed corrected-time series retains every B observation and its original timestamp alongside the corrected timestamp. Some corrected timestamps can fall outside the original recording boundaries; retain them and explain this rather than truncating source records. Alignment cannot certify calibration or cold-storage safety.
