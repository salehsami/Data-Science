# Odin Support Authorization — Prepared Input Starter

## Purpose
A fictional support-agent/customer FastAPI project with an **intentional broken object-level authorization defect**. Use only as a pre-recorded input after Odin approves the exact task. The correction, regression tests, and security report are **not** done.

## Setup (BEFORE recording only)
1. Open this folder in VS Code as the project root.
2. Create a virtual environment: `python3 -m venv .venv`, then `source .venv/bin/activate`.
3. Install: `python -m pip install -r requirements.txt`.
4. Initialize data: `python reset_db.py`.
5. Select `.venv/bin/python` as the VS Code interpreter.
6. Use **Run and Debug → Run Support API (GUI Debug)**; the server uses port 8001 to avoid the top-up project on port 8000.
7. Open `http://127.0.0.1:8001/docs` in Firefox for smoke checks. The API only has `/health` and `/customers/{customer_id}`.
8. In DBeaver create a SQLite connection to the **absolute path** to `support.db`, then inspect `agents` and `customers`.
9. Verify `/health` returns 200 and shut down the server through VS Code. Keep the defective starting code unchanged until the approved recording.

## Fictional test identities
- Agent `AG-001` token: `demo-token-alex` (owns `CUST-101`, `CUST-102`)
- Agent `AG-002` token: `demo-token-morgan` (owns `CUST-201`, `CUST-202`)
- These credentials are fictional demo credentials only, never reuse them anywhere else.

In Swagger `/docs`, open **GET /customers/{customer_id}**, click **Try it out**, type a customer ID, and put `Bearer demo-token-alex` in the `authorization` field. A request for `CUST-201` currently returns 200 even though `AG-001` does not own it. This is the **intentional starting defect**.

## Intended genuine recorded workflow (after approval)
- Demonstrate unauthorized cross-agent access through Firefox/Swagger.
- Investigate `agents` / `customers` and their ownership relation in DBeaver.
- Correct authorization logic in VS Code so only an owning agent can view the record; choose and document a consistent 403 or 404 unauthorized policy. No modification to stored ownership data should be required.
- Add regression tests covering owner success, cross-agent denial, missing/invalid token, and unknown ID; run and inspect results via approved VS Code functions.
- Retest in Firefox and run read-only SQL verification in DBeaver.
- Author a brief security validation report during the recording and save corrected app + tests + SQL + report as deliverables.

## Important Mercor constraints
- Do not record without approved idea AND approved apps. Confirm exact approval text in Studio and TaskRecorder.
- No AI assistance during recording; permitted AI-prepared inputs should be disclosed in Studio Final Notes.
- Restricted Terminal, Safari, Chrome, Preview, etc. must not be displayed during recording.
- The current starter does NOT include finished tests or a finished report. Don't portray preparation as recorded engineering work.
- If Odin approval text differs materially from the proposed task, align the project and goal before recording.
