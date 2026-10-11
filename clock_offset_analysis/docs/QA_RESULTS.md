# Software QA

Validation performed using disposable databases, not the recording database:
- Nine automated tests cover source counts/clean state, recovered simulation shift, identical candidate pair counts, window separation, missing-sample handling, fixed-offset validation, remaining bias, sign convention, invalid offsets, independent SQL search, HTTP routes, frozen validation, exports and packaging.
- All 24 SQL investigations execute against a completed temporary analysis.
- Independent SQL candidate search agrees with Python estimation.
- Independent raw-source reconstruction agrees with phase MAE, bias and correlation squared.
- Exported corrected B readings preserve all original temperatures and apply the documented timestamp sign.
- Export before validation and changing a frozen validation offset are rejected.
- Packaging rejects incomplete work and produces a valid archive for a completed QA fixture.
- Starter source counts are 480 per sensor; all output tables remain empty and no analysis exports are in the starter.

Browser JavaScript is syntax-checked. A DOM simulation also verifies initialization, candidate-row rendering, competing-offset preview, leader selection, SVG generation, locked validation/reveal and export confirmation. This tests control flow, not native browser layout. A native browser rendering/interaction test has not been completed in the build environment because a browser executable is unavailable. Before recording, confirm the charts and controls render in Firefox on the Mac. Use a separate project copy for any practice analysis/export.

Mac interpreter, VS Code extensions, DBeaver driver and exact Odin app/idea approval must be ready before recording. They cannot be verified by container tests.
