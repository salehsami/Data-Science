# Heat Sensor Planner — complete Odin starter

A local Python/SQLite tool for choosing a heat-monitoring pilot deployment: up to four sites, installation budget €1,000, maximum covered priority population at a 300 m planning radius. Firefox dashboard + DBeaver verification + VS Code recommendation.

**No extra Python packages, cloud accounts, API keys or external services.** Requires Python 3.9+, VS Code with Python/Debugger extensions, Firefox, and DBeaver with the SQLite driver. Those app components must be ready before recording.

## Start here
1. Read `docs/SETUP_AND_CONNECTIONS.md` and connect DBeaver to `data/heat_planning.db`.
2. Open this entire folder in VS Code.
3. Run and Debug → **Run Heat Sensor Dashboard (GUI)** → green triangle.
4. In Firefox open **http://127.0.0.1:8765**.
5. Follow `docs/RECORDING_PLAN.md` after exact idea/app approval.

The bundled database contains inputs only. No deployment has been chosen and no recommendation has been completed. Use a separate project copy for practice.

## Files
- `planner.py`: inclusive-radius coverage, exact subset enumeration and tie rules.
- `server.py`: local HTTP tool and CSV/SQLite exports; binds to localhost.
- `prepare_data.py`: repeatable fictional input preparation, optional explicit reset.
- `data/heat_planning.db`: input tables plus empty analysis tables.
- `data/candidate_sites.csv`, `data/demand_zones.csv`: original synthetic inputs.
- `web/index.html`: interactive map, candidate comparisons and fixed-site sensitivity.
- `sql/01_input_checks.sql`: input validity and inspection.
- `sql/02_verify_selection.sql`: independently reconstructed cost, population and per-zone coverage.
- `sql/03_fixed_deployment_sensitivity.sql`: same selected sites, three radii.
- `sql/04_independent_optimality.sql`: independent SQLite enumeration at 300 m.
- `templates/Deployment_Recommendation.md`: unfinished analyst memo.
- `docs/INPUT_BRIEF.md`: assumptions, provenance and output contract.
- `docs/SETUP_AND_CONNECTIONS.md`: GUI setup and troubleshooting.
- `docs/RECORDING_PLAN.md`: analysis sequence and narration cues.
- `docs/METHOD_AND_CODE.md`: method/code explanation.
- `docs/QA_RESULTS.md`: software validation evidence, not task analysis results.
- `package_deliverables.py`: packaging after recording.
- `tests/test_planner.py`: meaningful correctness checks using temporary databases.
- `.vscode/launch.json`: GUI run configurations; keep this folder when transferring.

## During analysis
A manual selection can be inspected without running a search. **Evaluate every feasible combination** computes ranked candidates on demand. **Save analysis files** exports the current feasible selection and writes it to SQLite for DBeaver checks. It may overwrite a previous export; save the final selection before verifying it. The application flags whether the saved selection matches the optimum. Interpret that evidence yourself.

Input data should not be edited while the dashboard is running: searches are cached by radius. Stop and restart the dashboard after an intentional source-data change. Do not change input records to manufacture a desired answer.

## Output location
All analysis exports are under `outputs/`. Complete the memo there as `Deployment_Recommendation.md`. The starter ZIP is not your final Deliverables.zip: the final archive must include your recorded work and completed memo.

## Verification
Run `python3 -m unittest discover -s tests -v` outside recording if desired. Tests use disposable data and do not complete the task in this project. Software QA has already been performed; see `docs/QA_RESULTS.md`.

## After recording
Use the **Package Deliverables (after recording)** launch configuration. It refuses to package if mandatory exports, saved SQLite analysis or a completed memo are missing. It creates `Deliverables.zip` in the project root with input, tool, intermediate analysis and final-output folders. Metadata.rtf and recording files stay outside that archive. Validate and upload the four items required by your current instructions.
