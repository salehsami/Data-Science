# Clock Offset Analysis — complete recording starter

A deterministic Python/SQLite tool to investigate disagreement between fictional colocated temperature sensors. Estimate a timestamp correction from the first three hours, freeze it, validate it on the final hour, verify independently in SQL, then write a diagnostic recommendation.

## Start
1. Extract this entire folder and open the inner `clock_offset_analysis` folder in VS Code.
2. Connect DBeaver to `data/sensors.db` (SQLite).
3. VS Code Run and Debug → **Run Clock Offset Dashboard (GUI)** → Start.
4. Open **http://127.0.0.1:8766** in Firefox.
5. Read `docs/START_HERE.md` before recording and `docs/RECORDING_AND_NARRATION.md` for the complete stage-by-stage workflow.

Python 3.9+, Microsoft's Python and Python Debugger extensions, Firefox and DBeaver's SQLite driver are required. **No additional Python packages, cloud accounts, API keys or internet access are required to run the analysis tool.** Initial installation of those app components is a separate prerequisite.

## Included
- `analysis.py`: common pairing grid, Pearson correlation, MAE, signed difference, candidate ranking and phase evaluation.
- `prepare_data.py`: reproducible synthetic input generator. It does not analyze or select an offset.
- `server.py`: localhost-only dashboard and exports.
- `web/index.html`: charts, candidate comparison, locked-offset validation and pairing audit.
- `data/sensors.db`: 960 raw readings plus empty analysis tables.
- `data/sensor_readings.csv`: original synthetic inputs.
- `sql/investigations.sql`: all 24 numbered read-only investigations.
- `templates/Diagnostic_Recommendation.md`: unfinished final-report template.
- `docs/START_HERE.md`: exact setup, recording order and troubleshooting.
- `docs/INPUT_BRIEF.md`, `docs/METHOD.md`: assumptions and implementation explanation.
- `docs/RECORDING_AND_NARRATION.md`: point-and-say practice guide with expected results.
- `docs/TASK_RECORDER.md`: proposed exact Goal, apps and disclosure.
- `docs/QA_RESULTS.md`: testing evidence and remaining environment checks.
- `Metadata.rtf`: prefilled reference; reconcile actual opening app, Goal and topology before upload.
- `package_deliverables.py`: checks completed work and creates Deliverables.zip after recording.
- `.vscode/launch.json`: GUI launch configurations.
- `tests/test_analysis.py`: independent correctness and integration checks using temporary files.

## Clean start
No analysis has been saved to this database. Its analysis tables are empty, `outputs` contains no final files, and the diagnostic recommendation is unfinished. Practice in a separate extracted copy; restart its server before a new session because validation freezes the selected offset. Do not complete the final deliverable in advance and reenact it during recording.

## Sign convention
**corrected B timestamp = original B timestamp + offset**. Pair A(t) with B(t − offset). A negative offset proposes moving B timestamps earlier. Correction affects timestamps only, never temperatures. The full corrected export retains all 480 B rows, including corrected timestamps falling before the original recording start.

## Stages
DBeaver source checks → Firefox original-series review → compare estimation offsets → choose from estimation evidence → freeze and validate → save → DBeaver independent verification → VS Code artifact inspection and completed recommendation.

After validation, do not retune the offset using the final-hour results. A disappointing validation result should be reported as such. The tool computes evidence; your final recommendation requires judgment and limitations.

## Testing and packaging
Outside recording, optional: `python3 -m unittest discover -s tests -v`. Tests use temporary databases, not the recording copy.

After recording, use **Package Deliverables (after recording)**. The completed memo must be saved at `outputs/Diagnostic_Recommendation.md` and every placeholder replaced. Upload Metadata.rtf, video and raw recording ZIP separately from Deliverables.zip.
