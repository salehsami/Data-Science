"""Ghost Customers — intentionally unfinished investigation starter.
Complete the TODOs during the approved recorded task.
No hidden bot labels or definitive fraud ground truth are provided.
"""
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'engagement.db'
OUTPUTS = ROOT / 'outputs'
SEED = 42


def load_data() -> pd.DataFrame:
    if not DB.is_file():
        raise FileNotFoundError(f'Missing database: {DB}')
    with sqlite3.connect(DB) as cn:
        events = pd.read_sql_query('SELECT * FROM events', cn)
    events['event_ts'] = pd.to_datetime(events['event_ts'], utc=True)
    return events


def validate(events: pd.DataFrame) -> None:
    needed = {'event_id', 'account_id', 'session_id', 'event_ts', 'event_type', 'page'}
    assert needed.issubset(events.columns), 'Missing required event fields'
    assert not events[list(needed)].isna().any().any(), 'Unexpected missing fields'
    assert events['event_id'].is_unique, 'Duplicate event IDs'
    print(f'Validation passed: {len(events):,} events, '
          f'{events.session_id.nunique():,} sessions')


def engineer_session_features(events: pd.DataFrame) -> pd.DataFrame:
    # TODO 1: Compute per-session counts, durations, rate per minute,
    # unique pages, search share, and inter-event timing variability.
    # Choose and explain how to handle zero-duration and 1-event sessions.
    raise NotImplementedError('TODO 1: session-level feature engineering')


def detect_anomalies(features: pd.DataFrame) -> pd.DataFrame:
    # TODO 2: Choose numerical feature columns and scale/transform where justified.
    # Fit IsolationForest(random_state=SEED, contamination=...)
    # Export an interpretable anomaly score and binary flagged indicator.
    raise NotImplementedError('TODO 2: anomaly detection')


def compare_with_rules(scored: pd.DataFrame) -> pd.DataFrame:
    # TODO 3: Define 2-3 transparent behavior rules and analyze disagreements
    # between rules and Isolation Forest. These are not confirmed bot labels.
    raise NotImplementedError('TODO 3: interpretable rule comparison')


def quantify_impact(events: pd.DataFrame, scored: pd.DataFrame) -> dict:
    # TODO 4: Compare raw event totals / sessions / events per session with
    # metrics excluding flagged sessions, and calculate flagged event share.
    # Discuss that an adjusted KPI is sensitive to flagging assumptions.
    raise NotImplementedError('TODO 4: KPI contamination assessment')


def write_outputs(scored: pd.DataFrame, metrics: dict) -> None:
    # TODO 5: Create outputs/session_anomaly_scores.csv with evidence columns.
    # TODO 6: Create outputs/engagement_audit.html with charts & KPI comparisons.
    # TODO 7: Create outputs/investigation_summary.md with decision and caveats.
    raise NotImplementedError('TODO 5-7: client deliverables')


def run() -> None:
    events = load_data()
    validate(events)
    print('Starter preflight complete. The investigation is not yet implemented.')
    # TODO: Complete and invoke the feature, modeling, comparison, KPI and output steps.


if __name__ == '__main__':
    run()
