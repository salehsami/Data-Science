"""Ghost Customers — COMPLETE REHEARSAL implementation.
Synthetic data only. Model flags are NOT verified bot labels.
Keep the recording starter unfinished and perform genuine investigation there.
"""
from pathlib import Path
import base64
import io
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'engagement.db'
OUTPUTS = ROOT / 'outputs'
SEED = 42
FEATURES = ['log_event_count', 'log_events_per_min', 'unique_pages',
            'search_share', 'mean_gap_sec', 'gap_cv']


def load_data() -> pd.DataFrame:
    if not DB.is_file():
        raise FileNotFoundError(f'Missing database: {DB}')
    with sqlite3.connect(DB) as cn:
        events = pd.read_sql_query('SELECT * FROM events', cn)
    events['event_ts'] = pd.to_datetime(events['event_ts'], utc=True)
    return events


def validate(events: pd.DataFrame) -> None:
    needed = {'event_id', 'account_id', 'session_id', 'event_ts', 'event_type', 'page'}
    assert needed.issubset(events.columns), 'Missing event columns'
    assert not events[list(needed)].isna().any().any(), 'Missing required values'
    assert events.event_id.is_unique, 'Duplicate event IDs'
    assert events.groupby('session_id').account_id.nunique().max() == 1, 'Multiple accounts per session'
    print(f'Validation passed: {len(events):,} events, {events.session_id.nunique():,} sessions')


def engineer_session_features(events: pd.DataFrame) -> pd.DataFrame:
    work = events.sort_values(['session_id', 'event_ts', 'event_id']).copy()
    work['gap_sec'] = work.groupby('session_id').event_ts.diff().dt.total_seconds()
    work['is_search'] = work.event_type.eq('search').astype(int)
    agg = work.groupby('session_id').agg(
        account_id=('account_id', 'first'), event_count=('event_id', 'size'),
        first_ts=('event_ts', 'min'), last_ts=('event_ts', 'max'),
        unique_pages=('page', 'nunique'), search_share=('is_search', 'mean'),
        mean_gap_sec=('gap_sec', 'mean'), std_gap_sec=('gap_sec', 'std'),
        gap_count=('gap_sec', 'count'),
    ).reset_index()
    agg['duration_sec'] = (agg.last_ts - agg.first_ts).dt.total_seconds()
    # Treat <=0 duration as undefined rate, rather than infinity.
    agg['events_per_min'] = np.where(
        agg.duration_sec > 0, 60.0 * agg.event_count / agg.duration_sec, np.nan)
    agg['gap_cv'] = np.where(
        (agg.gap_count >= 2) & (agg.mean_gap_sec > 0),
        agg.std_gap_sec / agg.mean_gap_sec, np.nan)
    agg['log_event_count'] = np.log1p(agg.event_count)
    agg['log_events_per_min'] = np.log1p(agg.events_per_min)
    assert agg.session_id.is_unique
    assert agg.event_count.sum() == len(events)
    print(f'Engineered {len(agg)} session feature rows; events reconciled.')
    return agg


def detect_anomalies(features: pd.DataFrame) -> pd.DataFrame:
    out = features.copy()
    # Missing rates and CVs indicate insufficient time information, not genuine zeroes.
    # Use training-population medians for numeric model imputation.
    matrix = out[FEATURES].replace([np.inf, -np.inf], np.nan)
    matrix = matrix.fillna(matrix.median()).fillna(0)
    model = IsolationForest(n_estimators=200, contamination=0.08, random_state=SEED)
    model.fit(matrix)
    # Higher score = more unusual. This is the negative of sklearn's score_samples.
    out['anomaly_score'] = -model.score_samples(matrix)
    out['model_flag'] = (model.predict(matrix) == -1)
    print(f'Isolation Forest flagged {int(out.model_flag.sum())} of {len(out)} sessions.')
    return out


def compare_with_rules(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    rate_cutoff = out.events_per_min.quantile(0.95)
    count_cutoff = out.event_count.quantile(0.75)
    # Data-derived thresholds are heuristics, not validated bot detectors.
    out['rule_fast'] = out.events_per_min.gt(rate_cutoff).fillna(False)
    out['rule_regular'] = ((out.event_count >= count_cutoff) &
                           out.gap_cv.notna() & (out.gap_cv < 0.15))
    out['rule_search_heavy'] = (out.event_count >= count_cutoff) & (out.search_share > 0.85)
    out['any_rule_flag'] = out[['rule_fast', 'rule_regular', 'rule_search_heavy']].any(axis=1)
    out['flag_agreement'] = np.select(
        [out.model_flag & out.any_rule_flag, out.model_flag & ~out.any_rule_flag,
         ~out.model_flag & out.any_rule_flag],
        ['model and rules', 'model only', 'rules only'], default='neither')
    print('Model/rule comparison:', out.flag_agreement.value_counts().to_dict())
    return out


def quantify_impact(events: pd.DataFrame, scored: pd.DataFrame) -> dict:
    raw_events, raw_sessions = len(events), len(scored)
    flagged = scored.loc[scored.model_flag]
    flagged_events, flagged_sessions = int(flagged.event_count.sum()), len(flagged)
    remaining_events = raw_events - flagged_events
    remaining_sessions = raw_sessions - flagged_sessions
    assert scored.event_count.sum() == raw_events
    assert remaining_sessions > 0
    metrics = dict(raw_events=raw_events, raw_sessions=raw_sessions,
                   raw_eps=raw_events / raw_sessions,
                   flagged_sessions=flagged_sessions, flagged_events=flagged_events,
                   flagged_event_pct=100.0 * flagged_events / raw_events,
                   adjusted_events=remaining_events,
                   adjusted_sessions=remaining_sessions,
                   adjusted_eps=remaining_events / remaining_sessions)
    print(f"Flagged-event share: {metrics['flagged_event_pct']:.2f}% | "
          f"events/session: {metrics['raw_eps']:.2f} -> {metrics['adjusted_eps']:.2f}")
    return metrics


def make_chart(scored: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    normal = scored.loc[~scored.model_flag]
    flagged = scored.loc[scored.model_flag]
    axes[0].scatter(normal.event_count, normal.events_per_min, s=10, alpha=.45, label='Unflagged')
    axes[0].scatter(flagged.event_count, flagged.events_per_min, s=17, alpha=.8, label='Model-flagged')
    axes[0].set(xlabel='Events per session', ylabel='Events per minute', title='Session behavior')
    axes[0].legend(fontsize=8)
    values = scored.flag_agreement.value_counts().reindex(
        ['model and rules', 'model only', 'rules only', 'neither'], fill_value=0)
    axes[1].bar(range(len(values)), values.values)
    axes[1].set_xticks(range(len(values)), ['Both', 'Model', 'Rules', 'Neither'], rotation=20)
    axes[1].set(ylabel='Session count', title='Detection agreement')
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=135, bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def write_outputs(scored: pd.DataFrame, metrics: dict) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    score_path = OUTPUTS / 'session_anomaly_scores.csv'
    scored.sort_values('anomaly_score', ascending=False).to_csv(score_path, index=False)
    chart = make_chart(scored)
    ranked = scored.sort_values('anomaly_score', ascending=False).head(12)
    table = ranked[['session_id', 'event_count', 'events_per_min',
                    'search_share', 'gap_cv', 'anomaly_score',
                    'model_flag', 'any_rule_flag']].round(3).to_html(index=False, border=0)
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Ghost Customers | Engagement Audit</title><style>
body{{font:16px system-ui,sans-serif;max-width:1100px;margin:40px auto;color:#202939;padding:0 22px}}
h1{{font-size:2.2rem}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.card{{background:#f0f4f8;border-radius:12px;padding:20px}}.number{{font-size:1.6rem;font-weight:bold}}
table{{border-collapse:collapse;width:100%;font-size:12px}}td,th{{border-bottom:1px solid #ddd;padding:8px;text-align:left}}
img{{width:100%}}.note{{background:#f5f6f8;padding:16px;border-left:3px solid #556}}
</style></head><body><h1>Ghost Customers: Engagement Audit</h1>
<p>Synthetic activity — unsupervised anomaly analysis. Flags are <strong>not</strong> verified bots.</p>
<div class="cards">
<div class="card">Raw events<div class="number">{metrics['raw_events']:,}</div></div>
<div class="card">Sessions flagged<div class="number">{metrics['flagged_sessions']:,} / {metrics['raw_sessions']:,}</div></div>
<div class="card">Events from flagged sessions<div class="number">{metrics['flagged_event_pct']:.2f}%</div></div>
<div class="card">Raw events/session<div class="number">{metrics['raw_eps']:.2f}</div></div>
<div class="card">Exclusion scenario events/session<div class="number">{metrics['adjusted_eps']:.2f}</div></div>
<div class="card">Unflagged sessions<div class="number">{metrics['adjusted_sessions']:,}</div></div>
</div><h2>Activity and detection comparison</h2><img alt="Behavior and agreement plots" src="data:image/png;base64,{chart}">
<h2>Highest anomaly scores</h2>{table}
<p class="note">Excluding flagged sessions is a sensitivity scenario, not a validated human-only KPI. Some legitimate power users or instrumented sessions may be flagged. Thresholds and contamination are assumptions.</p>
</body></html>'''
    (OUTPUTS / 'engagement_audit.html').write_text(html, encoding='utf-8')
    both = int((scored.model_flag & scored.any_rule_flag).sum())
    model_only = int((scored.model_flag & ~scored.any_rule_flag).sum())
    rules_only = int((~scored.model_flag & scored.any_rule_flag).sum())
    memo = f'''# Ghost Customers — Investigation Summary

## Objective
Investigate whether statistically unusual sessions disproportionately influence engagement reporting in a synthetic subscription-platform dataset.

## Data and method
- {metrics['raw_events']:,} events aggregated into {metrics['raw_sessions']:,} sessions.
- Session count, duration, intensity, page diversity, search share and interval variability.
- Isolation Forest with 200 trees, contamination 0.08, random seed 42. Model scores are not bot probabilities.
- Transparent, heuristic rules for event intensity, interval regularity and search concentration.
- Undefined single-event/zero-duration features were median-imputed **for modeling only**; original missing values remain in export.

## Results
- Model-flagged sessions: **{metrics['flagged_sessions']:,}** of **{metrics['raw_sessions']:,}**.
- Events in flagged sessions: **{metrics['flagged_events']:,}** (**{metrics['flagged_event_pct']:.2f}%** of raw events).
- Raw events per session: **{metrics['raw_eps']:.2f}**.
- Events per session after excluding model-flagged sessions: **{metrics['adjusted_eps']:.2f}**.
- Model-and-rule agreement: **{both}** sessions; model-only: **{model_only}**; rules-only: **{rules_only}**.

## Interpretation and recommendation
The difference between raw and exclusion-scenario engagement quantifies sensitivity to the model's flags, **not** confirmed fake engagement. Review top-ranked sessions with platform instrumentation and operational context, obtain verified labels, and evaluate false positives before adopting a production exclusion policy.

## Limitations
Unsupervised scores depend on engineered features, contamination and thresholds. High-frequency/regular interactions may reflect legitimate automation or logging artefacts. One session per account in this synthetic input is not representative of all real platforms. No ground-truth bot labels or causal claims are available.
'''
    (OUTPUTS / 'investigation_summary.md').write_text(memo, encoding='utf-8')
    print('Wrote:', score_path.name, 'engagement_audit.html', 'investigation_summary.md')


def run() -> None:
    events = load_data()
    validate(events)
    features = engineer_session_features(events)
    scored = detect_anomalies(features)
    scored = compare_with_rules(scored)
    metrics = quantify_impact(events, scored)
    write_outputs(scored, metrics)


if __name__ == '__main__':
    run()
