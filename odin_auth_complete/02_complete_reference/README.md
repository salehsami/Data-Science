# Support Records API — complete reference implementation

This folder is the **completed technical reference**. It is deliberately separate from `01_unfixed_starter`, which retains the original broken authorization code. Fictional data only.

## Prepare (outside the recorded session)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reset_db.py
```

## Start in VS Code

Open this folder and use **Run and Debug → Run Support API (GUI Debug)**.
Local URLs: `http://127.0.0.1:8001/health` and `http://127.0.0.1:8001/docs` (open using Firefox).

Swagger request examples for `GET /customers/{customer_id}`:

- Header `Authorization: Bearer demo-token-alex`, customer `CUST-101` → 200
- Header `Authorization: Bearer demo-token-alex`, customer `CUST-201` → 403
- Header `Authorization: Bearer demo-token-morgan`, customer `CUST-201` → 200
- Missing header → 401
- Header `Authorization: Bearer demo-token-alex`, customer `CUST-999` → 404

In Swagger's **Try it out**, the `authorization` input is a request-header field; include the full `Bearer ` prefix.

## Verify

Run `python -m pytest tests -q` from VS Code's pre-recording setup terminal, or from the VS Code Testing interface when recording, following Odin's app restrictions.

Run `python tools/generate_security_report.py` to execute the tests and create `outputs/security_validation.json` and `outputs/security_validation.html`. Inspect the HTML in Firefox.

Inspect `sql/ownership_verification.sql` in DBeaver against this directory's `support.db`.

## Design and limitations

A valid bearer token resolves to a server-side agent ID; the customer is retrieved with a parameterized query. Missing objects get 404, other owners get 403. The response body of a denied request does not contain private customer details.

Demonstration tokens are not production security. A production deployment would use a managed identity provider, token rotation, auditing, role policy reviews, TLS, and additional endpoint coverage.

## Mercor integrity reminder

The complete reference solution is for advance study and independent validation. Do not submit or film it as if you wrote the solution live. The approved task requires genuine recorded analysis, code changes, regression tests, and report creation. No AI interaction or content generation during recording. Keep the original starter unchanged until recorded work begins; disclose any AI-generated prepared input as required.
