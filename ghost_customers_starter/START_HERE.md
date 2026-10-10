# Ghost Customers — Odin recording starter

## Status

**Synthetic inputs ready; final investigation unfinished.** Use this as an approved-task starter, not a completed report. Run the current Odin idea and app approval check before recording.

## Scenario

A subscription platform suspects unusual sessions are inflating engagement statistics. As a data scientist, inspect event logs, engineer session behavior features, identify outliers, assess consistency with interpretable rules, and quantify the effect of exclusion on the reported engagement metrics. Outliers are **not proven bots**.

## Tools (three contributing apps)

1. **DBeaver** — connect to `data/engagement.db`, execute SQL diagnostics and inspect anomalous session patterns.
2. **Visual Studio Code** — implement session features, Isolation Forest analysis, rule comparison, KPI calculations, CSV and HTML/memo generation.
3. **Firefox** — open `outputs/engagement_audit.html`, inspect charts/table/metrics, validate stakeholder presentation.

## Files

- `data/engagement.db` — fictional 640 accounts/sessions and 31,981 events across September 2026 (fully synthetic).
- `build_dataset.py` — reproducible database generator, used **only for pre-recording preparation**. It encodes anomaly patterns but does **not** write hidden labels to the DB; don't inspect generator details in recording as substitute for analysis.
- `sql/investigation.sql` — one safe preflight query and unfinished investigation tasks.
- `src/analyze.py` — safe load/validate preflight and genuinely unfinished TODO analysis.
- `requirements.txt` — pandas, numpy, scikit-learn, matplotlib.
- `outputs/` — empty except `.gitkeep`, to hold final completed output.
- `docs/GOAL_FOR_APPROVAL_CHECK.txt` — earlier drafted wording **only**; the actual approved Odin Goal controls.

## Pre-recording setup on your Mac

1. Extract ZIP and open the folder in VS Code.
2. In VS Code's integrated terminal **before recording**: `python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install -r requirements.txt`.
3. Select the `.venv` Python interpreter in VS Code.
4. Connect DBeaver to the **absolute path** of `data/engagement.db`, using New Database Connection → SQLite → Browse → Test Connection → Finish. Confirm `accounts` and `events` tables.
5. Safe preflight from project root: `python src/analyze.py`; it should report 31,981 events and 640 sessions and say no analysis implemented.
6. Safe DBeaver preflight: run the first `SELECT` in `sql/investigation.sql`. Expect 640 accounts, 31,981 events, 640 sessions.
7. Confirm Firefox can open local `.html` files. Do not generate the final audit before recording.
8. Prepare the Goal-only opening document, and `Metadata.rtf` using Mercor's official template. Do not display metadata, chat, scripts, AI, or instructions during recording.
9. Confirm permissions, language, microphone, dock, clock, wallpaper, Accessibility Inspector and recording tools, per **current** Odin requirements.

## Suggested genuine recorded workflow (about 22–25 minutes)

- 0:00–0:20: Show Goal-only document and say required opening sentence. Intro brief.
- 0:20–7:00 **DBeaver:** source integrity, volume by date, top sessions, duration/event rate and composition; explain findings and hypotheses.
- 7:00–18:30 **VS Code:** implement features, choose IF settings, compare transparent rules, evaluate metrics, write scorecard, HTML, decision memo. Run validations and correct any observed errors.
- 18:30–22:00 **Firefox:** open report; verify charts/labels/metrics and anomalies; identify false-positive uncertainty.
- 22:00–24:00 **VS Code:** reconcile report and exports and finalize recommendations if needed.

Do not prolong the task to hit a duration. Finish actual, useful analysis and artifact review. The approved recorded workflow should create at least one finished client-usable deliverable.

## Analysis guide / interpretation

### A. SQL

- Missing data, duplicated event IDs, valid event types, account referential integrity.
- Top-session volume and share of all events.
- Session duration and events per minute; watch division by zero, sessions with same-second events.
- Contrast atypical timing, event type mix and visit patterns.

### B. Python session feature engineering

`event_count`, `duration_sec`, `events_per_min`, `unique_pages`, `search_share`, `mean_gap_sec`, `std_gap_sec`, `gap_cv` (std / mean with sensible zero handling). Apply transformations to heavy-tailed features when useful. Sort events chronologically first.

### C. Anomaly detector

Use `sklearn.ensemble.IsolationForest` with fixed random seed, explicit `contamination`, selected numeric features, and document chosen feature transformations. `score_samples` generally makes lower values more anomalous; orient the displayed score clearly. Compare to rules (e.g. unusually low gap variability at high event volume; extreme events/min; unusually high search share) and discuss disagreements.

### D. Impact

Report raw number of events/sessions, number flagged, total flagged events and percent of events flagged, and raw vs adjusted average events per session. Include how assumed contamination affects findings. Exclusion is a sensitivity analysis, not proof of inflated engagement.

### E. Outputs

`outputs/session_anomaly_scores.csv` — one row/session with features, scores, rule flags, and model flag.

`outputs/engagement_audit.html` — self-contained, locally viewable report with basic counts, suspicious activity examples, charts and raw/adjusted KPI comparisons.

`outputs/investigation_summary.md` — findings, assumptions, rule/model disagreements, risk of false positives and recommended human review or telemetry improvements.

## Verification requirements

- All 31,981 events map to 640 unique sessions; no duplicated/missing essential IDs.
- Sum of session event counts equals raw event count.
- Flagged + unflagged event totals equals raw event count.
- Recalculate flagged share from counts and reconcile exported CSV/HTML/memo.
- Verify scoring direction and explain that IF outliers are not definitively bots.
- Inspect generated HTML in Firefox, including charts and correct legends and units.

## Packaging

Store the database as input, SQL/Python as intermediate/working artifacts, and complete outputs in a `final output 1/` project directory if required by Studio. Ensure paths remain reproducible after extraction. Do not include `.venv` or caches. Keep `Metadata.rtf` out of `Deliverables.zip`. Upload separately the metadata, MP4, TaskRecorder original ZIP and deliverables ZIP, run both AutoQC sections and review results.

In Studio Final Notes disclose any AI-prepared inputs/scaffolds accurately (`AI-generated before recording`). Do not present completed AI-generated output as independently created in recording. Consult current instructions and reviewer feedback.
