# Recording plan — genuine analysis, target 20–25 minutes

This timing is an estimate, not a reason to pad or rush. Follow the current Odin instructions. Do not keep this guide, narration prompts, AI or metadata visible during recording. Do not record before idea/app approval. Perform each decision and verify actual results rather than reenacting a finished analysis.

## Opening — under 20 seconds
Show the exact approved Goal in an approved opening-document app. Say the required introduction from your checklist: “I will be beginning my task soon. Here is the workflow I have in mind.” Minimize the Goal document and begin work. Keep Dock and clock visible as required.

## 0:20–5:00 — DBeaver: source-data audit
Open `01_input_checks.sql`. Run the counts, uniqueness/validity checks, coordinate bounds and population total. Inspect site costs and high-population zones. Explain local metre coordinates and that zones form mutually exclusive population counts. Record what the results actually show.

Narration cues, not a script: Why are duplicate zones dangerous? Why would treating metre coordinates as latitude be wrong? Which constraints were agreed before optimization?

## 5:00–11:00 — Firefox: compare deployments
Keep the primary radius at **300 m**. Explore a manual deployment by selecting up to four sites. Observe cost, overlap and uncovered zones. Then click **Evaluate every feasible combination**. Inspect the top few ranked alternatives. Click a row to visualize its coverage. Explain why the cheapest sites or most sensors need not maximize covered population.

The ranked results are generated now by deterministic code. No final results are stored in the starter. Select a deployment supported by the primary objective; use **Select top-ranked deployment** if justified. Explain any cost/coverage tie. Do not claim a physical sensing range.

## 11:00–14:00 — Firefox: sensitivity and export
Inspect the **Fixed-deployment radius sensitivity** table. The same sites appear at 200, 300 and 400 m. Discuss sensitivity and uncovered zones. There is no need to change the primary radius selector to view these results. Finish the approved optimization at **300 m**.

Click **Save analysis files**. This writes five analysis files and the SQLite analysis tables. Inspect the confirmation. This does not write your recommendation.

## 14:00–19:00 — DBeaver: independent checks
Refresh the SQLite connection. Close stale data result tabs or open a new SQL editor if necessary. Run `02_verify_selection.sql`: constraints, independent covered population, exported summary, per-zone mismatch and overlap checks. Compare observed totals with Firefox. Run `03_fixed_deployment_sensitivity.sql` and compare all three radii. Run `04_independent_optimality.sql` if time permits; it uses an independent bit-mask enumeration and should agree with the dashboard top-ranked deployment at 300 m.

## 19:00–25:00 — VS Code: finish and inspect deliverables
Open `outputs/selected_sites.csv`, `zone_coverage.csv` and `fixed_deployment_sensitivity.csv`. Confirm headers and values. Complete the recommendation template with observed facts, your alternative comparison, independent verification and limitations. Save as `outputs/Deployment_Recommendation.md` and inspect its Markdown preview. This written judgment is part of the professional task; do not leave placeholders.

Close with a concise statement of what was saved and how it was checked. Stop TaskRecorder and wait for archiving. Package only after recording ends.

## Planned topology (replace with actual visit order)
1. Approved opening-document app — LOOKUP.
2. DBeaver — LOOKUP (source audit).
3. Firefox — CREATE (comparison, site selection, sensitivity and exports).
4. DBeaver — LOOKUP (independent verification).
5. VS Code — CREATE/MODIFY (verification SQL if changed; completed recommendation), LOOKUP (exports).

Add any actual returns and visits, including VS Code server launch if performed during recording. DBeaver queries are read-only; Firefox's save updates analysis tables. Use the exact official metadata categories.

## What must remain unfinished before recording
Source audit, primary search, site selection, sensitivity interpretation, final exports, analysis tables and written recommendation. Inputs, dependencies, app connections and the deterministic analysis tool may be prepared as disclosed.
