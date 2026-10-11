# Setup before recording — approximately 5–10 minutes if the apps are ready

Confirm the exact idea and all task apps are approved before recording. This starter follows the proposed Goal; if the approved wording differs, reconcile scope before starting. Do not display this guide during recording.

## 1. Extract and open the correct folder
1. Extract the ZIP to your Mac using the normal file interface.
2. In Visual Studio Code choose **File → Open Folder**.
3. Select the inner `heat_sensor_planner` folder. Its top level contains `server.py`, `planner.py`, `data`, `sql` and `.vscode`.
4. Trust this folder only after reviewing the supplied code.
5. Confirm Microsoft's **Python** and **Python Debugger** extensions are installed and enabled, and Python 3.9 or later is installed. No Python packages need installing.
6. Select the installed Python interpreter using VS Code's interpreter selector. If needed use **View → Command Palette → Python: Select Interpreter**. Pick Python 3, not an unrelated environment.

## 2. Connect DBeaver to SQLite
1. Open DBeaver; choose **Database → New Database Connection** (or its plug icon).
2. Search/select **SQLite**, then **Next**.
3. Beside the database path select **Browse/Open**. Choose `heat_sensor_planner/data/heat_planning.db` in your extracted folder.
4. Test the connection; if prompted to download the SQLite driver, do it before recording.
5. Finish. Expand the connection → Tables. Confirm `candidate_sites` and `demand_zones` are visible.
6. Analysis tables `selected_sites`, `zone_coverage`, `analysis_settings` should initially be empty. Do not solve/export yet if you want a clean starting state.
7. Open supplied `.sql` files with **SQL Editor → Open SQL Script** (menu wording can vary). Associate each editor with this SQLite connection using the connection selector.
8. During recording run one selected statement at a time with the Execute SQL Statement toolbar button. If using shortcuts, explain them aloud.

## 3. Start the dashboard without Terminal
1. In VS Code click **Run and Debug** in the left sidebar.
2. Select **Run Heat Sensor Dashboard (GUI)** from the dropdown.
3. Click the green start triangle. Python launches in the Debug Console.
4. In **Firefox**, open **http://127.0.0.1:8765**.
5. Confirm the heading is Heat Sensor Planner, there are 12 sites and no selection. Keep Python running in VS Code while using Firefox or DBeaver.

If no launch dropdown appears, confirm the whole inner project folder is open, the `.vscode/launch.json` file exists, and the Python Debugger extension is enabled. Reload VS Code if required. If port 8765 is in use, stop an older instance using its VS Code stop button.

## 4. Prepare the recommendation
Open `templates/Deployment_Recommendation.md`. It is intentionally unfinished. During recording complete it with observed results, then use **File → Save As** to save `outputs/Deployment_Recommendation.md`. Use VS Code's Markdown preview to inspect the final memo. Do not create a completed memo beforehand.

## 5. Opening and metadata
Prepare the exact approved Goal in a currently permitted opening-document app outside recording. This package deliberately does not invent a Mercor Metadata.rtf template or claim an Approval ID. Use the official template and the exact approved Goal for Metadata.rtf, Studio and TaskRecorder. See `RECORDING_PLAN.md` for a planned app sequence; metadata must reflect actual visits.

## Recovering after practice — before recording only
Practice on a separate copy of the project. If you practiced in the recording copy, stop the server, disconnect DBeaver, and reset before recording. The optional command `python3 prepare_data.py --reset` recreates fictional inputs and deletes files in `outputs` (except `.gitkeep`). Use VS Code's integrated terminal outside recording if appropriate; never run this after recording or after producing work you need to keep. Alternatively extract a fresh starter copy and reconnect DBeaver to its database.

A browser reload clears the screen selection but does not erase previously exported files or analysis tables. A fresh extracted copy is the easiest clean start.
