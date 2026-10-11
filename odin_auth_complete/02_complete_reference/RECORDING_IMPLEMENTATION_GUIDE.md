# Technical implementation and evidence checklist

## Before recording
- Obtain Studio task and match the approved Goal exactly.
- Open `01_unfixed_starter` for real work (not the completed reference).
- Start with a clean `support.db`; preserve the original database as an input.
- Configure VS Code debug, Firefox localhost Swagger, and DBeaver SQLite connection.
- Do not show this document, other Mercor materials, or AI during recording.

## Genuine workflow
1. In Firefox, reproduce the cross-agent access defect (`demo-token-alex` → CUST-201 returns 200).
2. In DBeaver, verify that CUST-201 belongs to AG-002, and CUST-101 to AG-001.
3. In VS Code, inspect `authenticate()` and `customer_record()` in `app/main.py`.
4. Decide 403 for authenticated users querying another owner's record. Add ownership check after customer exists and before return.
5. Build pytest `TestClient` regression tests with a separate temporary SQLite DB (do not damage recorded source data).
6. Test 200 own customer; 403 other owner in both directions; 401 missing/invalid token; 404 unknown; health 200.
7. Run tests in VS Code Testing UI and correct any actual failures.
8. Check the SQL owner mapping in DBeaver and re-run critical requests in Firefox.
9. Produce a factual validation report with only measured test results, include limitations.
10. Save files, verify output and close with natural narration.

## Final files
- Corrected FastAPI application and dependencies
- Regression test suite
- SQL ownership verification queries
- Security validation report and verification data
- Synthetic database and original inputs, per naming convention

## Important
The `02_complete_reference` folder is a separate technical reference, NOT a replacement for the actual recorded work. Follow the project's prepared-input disclosure rules and don't present prebuilt final content as created during the recording.
