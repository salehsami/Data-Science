# Software validation — starter package

These checks validate the tool using disposable copies. They are not the recorded task's final analysis or recommendation.

## Passed
- Eight automated unit tests: empty input state, radius boundary inclusion, overlap deduplication, exhaustive-search count and constraints, independently enumerated optimum, deterministic tie rules, fixed-deployment sensitivity, independent SQL optimum, and invalid-input handling. Some tests cover more than one property.
- Exact optimizer evaluates 794 subsets of up to four of the 12 sites.
- Independent Python bit-mask enumeration agrees with the optimizer.
- Independent SQLite bit-mask enumeration agrees with the optimizer.
- Local HTTP input, page, optimization and export endpoints tested in an isolated copy.
- Selected-site and zone-coverage CSVs and JSON export generated and inspected in the isolated copy.
- All post-selection verification queries executed; constraints passed, per-zone mismatches were absent and independently reconstructed population matched the dashboard backend.
- Fixed-deployment SQL sensitivity agreed with increasing-radius coverage.
- Packaging refused incomplete work; accepted a completed QA fixture; resulting ZIP passed archive-integrity verification. QA fixture outputs are excluded from the starter.
- Browser JavaScript passed Node syntax validation.
- Starter SQLite integrity check passed; all three analysis tables are empty and no final output files are present.

## Remaining local check
A browser rendering/interaction test could not run in the build environment because a browser executable was unavailable and its download failed. Before recording, open the dashboard in Firefox on the Mac and confirm the map, checkboxes and controls render. Use a separate practice copy if testing search/export; preserve the recording copy's clean starting state.

The Mac's installed Python interpreter, VS Code extensions, SQLite driver and Odin app approval are environment prerequisites, not verified by container tests. Recording duration is an estimate dependent on genuine analysis and familiarity.
