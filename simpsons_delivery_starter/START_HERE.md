# Simpson's Paradox — Delivery Algorithm Investigation

## Scope
Approved task: observational analysis of a fictional dispatch algorithm, not an A/B test. The dataset has 2,000 fictional deliveries and deliberately different delivery-distance composition by version. No final analysis/results have been run or exported in this starter. Approved task wording in Odin/Studio is authoritative; if different from planning text, use the exact approved wording.

## Step 0: Before recording (do this now)
1. Download/unzip the folder. Open `simpsons_delivery_starter` in VS Code using **File > Open Folder**.
2. Check your live Odin app catalogue: DBeaver, VS Code, Firefox and the app for opening the Goal document must all be permitted for this task. Do not use Terminal during the recording if restricted.
3. Python environment: use VS Code's integrated terminal **before recording** only for environment setup (subject to current policy):
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `python -m pip install -r requirements.txt`
   - `python build_dataset.py` (optional: recreates same DB; do NOT run during recording unless necessary)
   - Select `.venv` Python interpreter in VS Code.
4. DBeaver: **Database > New Database Connection > SQLite**; SQLite database file is `data/deliveries.db` (absolute path if needed). Click **Test Connection**, then **Finish**. Open SQL Editor and load `sql/investigation.sql`.
5. Firefox: confirm you can open local `file:///.../outputs/` HTML files once created. No need to open a final report yet.
6. Prepare a Goal-only opening document in a currently approved app, using the **exact approved Goal** copied from Studio. Do not show this guide/metadata in recording. For the TaskRecorder introduction, follow the latest Odin instructions.
7. Make `Metadata.rtf` from Mercor's official template *before* recording. **Request** must equal exact approved Goal; Topology must list chronological app visits, including repeats; Task Description numbered workflow. Do not display metadata while recording.
8. Start with SQL TODOs and Python TODOs unfinished. Keep `outputs/` empty until recording.

## Step 1: During recording — DBeaver (about 5–7 min)
1. Narrate: stakeholder wants to know whether new dispatch version really underperforms or just has a harder delivery mix.
2. Run prepared `COUNT`/distinct/flag-validity check.
3. Fill and run overall comparison:
```sql
SELECT algorithm_version, COUNT(*) AS n,
       ROUND(100.0 * AVG(on_time),2) AS on_time_pct
FROM deliveries GROUP BY algorithm_version;
```
4. Fill and run segmented comparison:
```sql
SELECT algorithm_version, distance_category, COUNT(*) AS n,
       ROUND(100.0 * AVG(on_time),2) AS on_time_pct
FROM deliveries
GROUP BY algorithm_version, distance_category
ORDER BY distance_category, algorithm_version;
```
5. Find the algorithm-specific mix:
```sql
SELECT algorithm_version, distance_category, COUNT(*) AS n,
ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY algorithm_version),2) AS mix_pct
FROM deliveries GROUP BY algorithm_version, distance_category;
```
6. Validate row-level consistency:
```sql
SELECT COUNT(*) AS inconsistent
FROM deliveries
WHERE on_time != CASE WHEN delivery_minutes <= promised_minutes THEN 1 ELSE 0 END;
```
7. Explain the paradox in your own words. Remember the SQL results, don't treat the invented mix as evidence of real-world causation.

## Step 2: During recording — VS Code (about 8–10 min)
Edit `src/analyze.py`. Keep work authentic; never paste a finished pre-generated investigation. Suggested statistical approach:

1. Load `df`; compute observed rates (`df.groupby('algorithm_version').on_time.mean()`) and category-by-algorithm rates (`groupby(['algorithm_version','distance_category'])`).
2. Compute **common pooled** distance weights: `weights = df.distance_category.value_counts(normalize=True)`.
3. For each algorithm, align segment rate indices to pooled weight indices, then compute `sum(weight[category] * rate[algorithm,category])`. This is **direct standardization**.
4. Compare `New - Old` *raw* rate difference against `New - Old` *standardized* rate difference in percentage points. A sign reversal is the key phenomenon.
5. For uncertainty, apply a **stratified bootstrap**: repeatedly resample deliveries with replacement **within each algorithm x category cell**; calculate category rates and apply the same fixed pooled weights. Use a deterministic generator (`numpy.random.default_rng(42)`); take 2.5th and 97.5th percentiles of the New-minus-Old standardized difference. Optional small B (e.g. 500) for speed.
6. Create `outputs/segment_comparison.csv` with counts, on-time rates and weights; `outputs/investigation_summary.md` with the raw/adjusted percentage-point gaps, bootstrap interval, conclusions and limitations.
7. Generate `outputs/delivery_report.html` **during recording** with a clear table + two charts (overall raw/adjusted rates and per-segment rates). matplotlib can export PNGs to `outputs/`, then embed relative images in the HTML. Alternatively, create a static HTML report with tables and CSS bars.
8. Open saved files and check values before moving to Firefox.

## Step 3: During recording — Firefox (about 3–4 min)
1. File > Open File; choose `outputs/delivery_report.html`.
2. Inspect overall and standardized comparison and category rates. Check units, legend, and correct New/Old labels.
3. Explain why the overall number can be misleading and why observational standardization is **not** proof of a causal algorithm effect.
4. If you spot an issue, return to VS Code, fix, re-run, and refresh Firefox.

## Step 4: Finish and verify (about 2–3 min)
- All 2,000 rows accounted for, no duplicate IDs, zero duration/flag inconsistencies.
- Per-version segment counts sum to overall counts.
- Pooled weights sum to 1; both algorithms use identical weights.
- Difference calculations use consistent percentage points.
- Fixed-weight bootstrap uses samples within each version-category cell; no changing weights per replicate.
- CSV/report/memo values agree. Re-open finished files.
- Final recommendation should mention potential confounding (location/time/driver differences), observational design and need for controlled validation.
- Stop recording per TaskRecorder workflow and verify recording archive afterward.

## Post-recording packaging
Create `Deliverables.zip` containing input database, meaningful source code/SQL, exported CSV/HTML/images, decision memo. Keep `Metadata.rtf` separate. Submit it alongside `video.mp4` and TaskRecorder archive ZIP and metadata in Studio. Disclose `AI-generated before recording` for synthetic database/scaffold in Studio Final Notes, per your checklist.

## Notes
- Use current Odin/Studio instructions if they conflict with this guide.
- Browser-app approval still matters; Firefox is a genuine report-validation step, not a filler app.
- Don't display this instruction document, AI interactions, Studio or Mercor guidance during recording.
- The fixture has deliberately structured behavior. A strong narrative requires discovering it from analysis, not pretending the fixture is real-world evidence.
