# Start here — complete setup and recording workflow

This starter implements the proposed clock-offset Goal. Confirm that the idea and three task apps are approved, and that the approved wording matches `TASK_RECORDER.md`, before recording. You do not need to write application code. The genuine recorded work is the data audit, estimation decision, fixed-offset validation, independent checks and completed recommendation.

## 1. Extract the ZIP
Extract to a normal local Mac folder. Open the **inner `clock_offset_analysis` folder** in VS Code using File → Open Folder. The folder must directly contain `server.py`, `analysis.py`, `data`, `web`, `sql` and `.vscode`.

Install/enable Microsoft's Python and Python Debugger extensions if not already present. Select your installed Python 3.9+ interpreter. There are no pip packages to install. Use View → Command Palette → Python: Select Interpreter if the interpreter selector is not visible.

## 2. DBeaver connection
1. Database → New Database Connection → SQLite → Next.
2. Browse to **`data/sensors.db` inside your extracted folder**.
3. Test Connection; download the SQLite driver if prompted, before recording.
4. Finish and expand Tables. `readings` should contain 960 rows: 480 A and 480 B.
5. `candidate_scores`, `phase_metrics`, `aligned_pairs` and `analysis_settings` must be empty in the recording copy.
6. SQL Editor → Open SQL Script → select `sql/investigations.sql`. Associate the editor with this SQLite connection.
7. During recording, highlight ONE complete numbered statement, then click Execute SQL Statement. Do not execute the whole script before the analysis is saved.

## 3. Launch without Terminal
1. VS Code → Run and Debug.
2. Dropdown → **Run Clock Offset Dashboard (GUI)**.
3. Click the green start triangle. Keep the server running.
4. Firefox → **http://127.0.0.1:8766**.
5. Confirm Clock Offset Analysis appears, validation is hidden and no offset is selected.

No dropdown? Open the entire inner project folder, confirm `.vscode/launch.json` exists, and enable the Python Debugger extension. Reload VS Code if necessary.

Connection refused? Check that the VS Code server is running, use **http**, and use port **8766**, not the heat-planner port 8765. Port in use? Stop an older instance with VS Code's red stop button. Inspect Debug Console errors before starting a new instance.

## 4. Goal-only opening document
In Firefox use File → Open File and select `docs/Goal.html`. It contains only the proposed Goal. Confirm it exactly matches your approved Goal; update it before recording if necessary. Your opening document and dashboard can occupy separate Firefox tabs. Have the Goal tab active at the start, then move to DBeaver after the short introduction. Return to the dashboard tab when its analysis begins.

Use Firefox for this opening document only if it meets your current Odin opening-document instructions. If your task requires another specific approved opening app, use that app and update Metadata.rtf accordingly.

Keep Dock and clock visible, required background apps ready, irrelevant/private windows closed, and AI/script/metadata documents out of view. Complete your usual TaskRecorder preflight.

## 5. Recording sequence
1. Goal-only opening; required introduction under 20 seconds.
2. DBeaver: numbered queries **01–11**.
3. Firefox: inspect original estimation series and sign convention.
4. Click **Compare offsets — estimation only**.
5. Inspect leading and competing candidates; choose an offset from estimation evidence. **Select estimation leader** is available but the choice needs explanation.
6. Inspect proposed alignment, residual bias and the pairing example.
7. Click **Freeze offset and validate**. Selection becomes locked; final-hour results are revealed.
8. Interpret validation without retuning; click **Save analysis files**.
9. DBeaver: refresh/reconnect, then queries **12–24**.
10. VS Code: inspect exports, complete the recommendation and save as **`outputs/Diagnostic_Recommendation.md`**. Use Markdown preview for final inspection.
11. Stop TaskRecorder and wait for archiving.
12. After recording, run **Package Deliverables (after recording)** in VS Code.

Follow `RECORDING_AND_NARRATION.md` for specific pointers and spoken explanations. The target 20–25 minutes is an estimate; do not pad or rush genuine work.

## 6. What you must complete during recording
The application is ready, but the data audit, candidate comparison, offset choice, validation, final exports, SQL verification and recommendation remain unfinished. Do not submit the starter ZIP as the completed deliverable.

## 7. Practice and clean reset
Practice in a **separate extracted copy**. Stop its server before running the recording copy because both use port 8766. DBeaver must point to the recording copy's database, not the practice one.

After validation, the server freezes the selected offset. A page reload does not unfreeze the server. For a new practice session stop and restart the server. A fresh extracted project is the easiest clean recording start.

Optional reset outside recording: stop the server, disconnect DBeaver, then `python3 prepare_data.py --reset`. This deletes saved output files and rebuilds inputs. Do not reset after producing work you need to preserve.

## 8. Final files and uploads
Save creates five files in `outputs`: candidate_offsets.csv, phase_metrics.csv, aligned_pairs.csv, corrected_sensor_b.csv and analysis_summary.json. Your completed Diagnostic_Recommendation.md is the sixth required output.

The packaging configuration checks these files and creates Deliverables.zip containing inputs, executable tool, SQL, completed analysis database, analysis exports and recommendation. Its report check rejects unfinished placeholders. Inspect the ZIP after creation.

Upload four items separately according to your current guide: Metadata.rtf, video.mp4, TaskRecorder recording archive ZIP, Deliverables.zip. Metadata.rtf stays outside Deliverables.zip. Update topology to actual visits, and disclose **AI-generated before recording** in Final Notes for prepared inputs.
