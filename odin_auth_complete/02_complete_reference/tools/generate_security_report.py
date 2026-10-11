"""Export an offline HTML validation report from real regression test execution.

Usage: python tools/generate_security_report.py
The script executes pytest, writes a JSON summary, and renders an HTML file.
Do not label tests 'passed' unless execution has actually succeeded.
"""
from datetime import datetime, timezone
from pathlib import Path
from html import escape
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)
command = [sys.executable, "-m", "pytest", "tests/test_authorization.py", "-q"]
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
transcript = (result.stdout + "\n" + result.stderr).strip()
payload = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "verification_command": " ".join(command[1:]),
    "exit_code": result.returncode,
    "status": "PASS" if result.returncode == 0 else "FAIL",
    "test_output": transcript,
    "scope": "Synthetic local customer API; no real identities",
    "remaining_limitations": [
        "Demo tokens are static and stored in SQLite; use a real identity provider in production.",
        "Only the customer-read endpoint is in scope.",
        "Object existence is disclosed by 403 for an unauthorized existing record; 404 masking is an alternative policy.",
    ],
}
(OUTPUT / "security_validation.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
result_html = escape(transcript)
limitations = "".join(f"<li>{escape(x)}</li>" for x in payload["remaining_limitations"])
page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>Customer API — Authorization Verification</title>
<style>body{{font-family:system-ui,Arial,sans-serif;max-width:880px;margin:45px auto;padding:0 20px;color:#243044}}
h1{{margin-bottom:2px}}.small{{color:#64748b}}.status{{font-weight:700;padding:12px;background:#eff6ff;border-radius:8px}}
pre{{white-space:pre-wrap;background:#f1f5f9;padding:18px;border-radius:8px;overflow-wrap:anywhere}}
@media print{{body{{margin:15mm auto}}}}</style></head><body>
<h1>Customer API Authorization — Validation Report</h1>
<p class='small'>Generated: {escape(payload['generated_utc'])}</p>
<p>Scope: Synthetic support-record API. Server-side record ownership is evaluated after bearer-token authentication.</p>
<p class='status'>Automated verification result: {payload['status']}</p>
<h2>Regression test output</h2><pre>{result_html}</pre>
<h2>Policy validated</h2><p>Owned record: 200; cross-agent record: 403; missing/invalid token: 401; nonexistent record: 404.</p>
<h2>Remaining limitations</h2><ul>{limitations}</ul></body></html>"""
(OUTPUT / "security_validation.html").write_text(page, encoding="utf-8")
print(f"Test status: {payload['status']} (exit {result.returncode})")
print(f"Report: {OUTPUT / 'security_validation.html'}")
raise SystemExit(result.returncode)
