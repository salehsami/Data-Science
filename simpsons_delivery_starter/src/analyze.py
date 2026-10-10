"""Simpson's paradox delivery investigation — completed PRACTICE version.

Run in a COPY of the starter project, from VS Code's Run Python File command.
Dependencies: pandas, numpy, matplotlib (see requirements.txt).
"""
from pathlib import Path
import base64
import io
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "deliveries.db"
OUT = ROOT / "outputs"
CATEGORIES = ["Short", "Medium", "Long"]
VERSIONS = ["Old", "New"]
BOOTSTRAP_REPS = 2000
RANDOM_SEED = 42


def load_data():
    if not DB.is_file():
        raise FileNotFoundError(f"Database not found: {DB}")
    with sqlite3.connect(DB) as conn:
        return pd.read_sql_query("SELECT * FROM deliveries", conn)


def validate(df):
    required = {"delivery_id", "algorithm_version", "distance_category", "on_time",
                "delivery_minutes", "promised_minutes"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df.empty or df.delivery_id.isna().any() or df.delivery_id.duplicated().any():
        raise ValueError("No records, missing IDs, or duplicate delivery IDs")
    if df[list(required)].isna().any().any():
        raise ValueError("Nulls found in required fields")
    if not set(df.algorithm_version).issubset(VERSIONS):
        raise ValueError("Unexpected algorithm version")
    if not set(df.distance_category).issubset(CATEGORIES):
        raise ValueError("Unexpected distance category")
    if not set(df.on_time.unique()).issubset({0, 1}):
        raise ValueError("on_time must be 0 or 1")
    expected = (df.delivery_minutes <= df.promised_minutes).astype(int)
    if not expected.eq(df.on_time).all():
        raise ValueError("on_time contradicts actual and promised durations")
    for version in VERSIONS:
        for category in CATEGORIES:
            if df[(df.algorithm_version == version) & (df.distance_category == category)].empty:
                raise ValueError(f"Missing group: {version}/{category}")


def summarize(df):
    overall = (df.groupby("algorithm_version")["on_time"]
               .agg(n="size", rate="mean").reindex(VERSIONS))
    segments = (df.groupby(["algorithm_version", "distance_category"])["on_time"]
                .agg(n="size", rate="mean")
                .reindex(pd.MultiIndex.from_product([VERSIONS, CATEGORIES],
                                                    names=["algorithm_version", "distance_category"])))
    pooled_weights = (df.distance_category.value_counts()
                      .reindex(CATEGORIES).div(len(df)))
    if not np.isclose(pooled_weights.sum(), 1.0):
        raise AssertionError("Weights do not sum to one")

    by_category = segments["rate"].unstack("distance_category")[CATEGORIES]
    adjusted = by_category.mul(pooled_weights, axis=1).sum(axis=1)
    raw_diff = float(overall.loc["New", "rate"] - overall.loc["Old", "rate"])
    adjusted_diff = float(adjusted.loc["New"] - adjusted.loc["Old"])
    return overall, segments, pooled_weights, adjusted, raw_diff, adjusted_diff


def bootstrap_adjusted_diff(df, weights):
    """Resample independently within each version/category; hold pooled weights fixed."""
    rng = np.random.default_rng(RANDOM_SEED)
    groups = {(version, category): df.loc[
        (df.algorithm_version == version) & (df.distance_category == category),
        "on_time"].to_numpy(dtype=float)
        for version in VERSIONS for category in CATEGORIES}
    differences = np.empty(BOOTSTRAP_REPS)
    for i in range(BOOTSTRAP_REPS):
        adjusted_rates = {}
        for version in VERSIONS:
            adjusted_rates[version] = sum(
                float(weights.loc[category]) * rng.choice(
                    groups[(version, category)], size=len(groups[(version, category)]),
                    replace=True).mean()
                for category in CATEGORIES)
        differences[i] = adjusted_rates["New"] - adjusted_rates["Old"]
    return np.quantile(differences, [0.025, 0.975])


def make_chart(overall, segments, adjusted):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    x = np.arange(2)
    width = 0.34
    for i, (name, rates) in enumerate([
        ("Raw", overall["rate"]), ("Adjusted", adjusted)
    ]):
        axes[0].bar(x + (i - .5) * width, [rates.loc[v] * 100 for v in VERSIONS],
                    width, label=name)
    axes[0].set_xticks(x, VERSIONS)
    axes[0].set_ylim(0, 105)
    axes[0].set_ylabel("On-time deliveries (%)")
    axes[0].set_title("Overall vs distance-adjusted")
    axes[0].legend()
    for i, version in enumerate(VERSIONS):
        rates = segments.loc[version, "rate"].reindex(CATEGORIES)
        axes[1].bar(np.arange(3) + (i - .5) * width, rates.to_numpy() * 100,
                    width, label=version)
    axes[1].set_xticks(np.arange(3), CATEGORIES)
    axes[1].set_ylim(0, 105)
    axes[1].set_ylabel("On-time deliveries (%)")
    axes[1].set_title("Within each distance category")
    axes[1].legend()
    fig.tight_layout()
    image_buffer = io.BytesIO()
    fig.savefig(image_buffer, format="png", dpi=135, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(image_buffer.getvalue()).decode("ascii")


def write_outputs(overall, segments, weights, adjusted, raw_diff, adjusted_diff, ci):
    OUT.mkdir(parents=True, exist_ok=True)
    result = segments.reset_index()
    result["pooled_weight"] = result.distance_category.map(weights)
    result["mix_pct"] = result["n"] / result.groupby("algorithm_version")["n"].transform("sum") * 100
    result["on_time_pct"] = result["rate"] * 100
    result["weighted_contribution_pp"] = result["rate"] * result["pooled_weight"] * 100
    result.to_csv(OUT / "segment_comparison.csv", index=False, float_format="%.6f")

    chart = make_chart(overall, segments, adjusted)
    rows = result[["algorithm_version", "distance_category", "n", "mix_pct", "on_time_pct"]].copy()
    rows = rows.rename(columns={"algorithm_version": "Algorithm", "distance_category": "Distance",
                                "n": "Deliveries", "mix_pct": "Mix (%)", "on_time_pct": "On-time (%)"})
    html_table = rows.to_html(index=False, float_format=lambda x: f"{x:.2f}", classes="detail")
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1"><title>Delivery performance investigation</title>
    <style>body{{font-family:system-ui,Arial,sans-serif;max-width:1060px;margin:35px auto;padding:0 20px;color:#15283a;background:#f7f9fc}}
    h1{{font-size:30px}} .lead{{color:#52677b}} .metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}}
    .tile,.panel{{padding:20px;border-radius:14px;background:white;box-shadow:0 2px 12px #0001;margin:18px 0}}
    .num{{font-size:25px;font-weight:750}}.sub{{color:#667; font-size:13px}} img{{max-width:100%;height:auto}}
    table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #e0e5ee;text-align:left}}
    @media(max-width:700px){{.metrics{{grid-template-columns:1fr}}}}</style></head><body>
    <h1>Dispatch algorithm: a misleading aggregate?</h1><p class="lead">Synthetic observational data · Common-weight distance standardization</p>
    <div class="metrics"><div class="tile">Raw New − Old<div class="num">{raw_diff*100:+.2f} pp</div></div>
    <div class="tile">Adjusted New − Old<div class="num">{adjusted_diff*100:+.2f} pp</div></div>
    <div class="tile">95% bootstrap interval<div class="num">[{ci[0]*100:+.2f}, {ci[1]*100:+.2f}] pp</div></div></div>
    <div class="panel"><h2>Two ways to compare performance</h2><img alt="Charts comparing raw and adjusted algorithm performance and performance by distance" src="data:image/png;base64,{chart}"></div>
    <div class="panel"><h2>Distance group breakdown</h2>{html_table}</div>
    <div class="panel"><h2>Interpretation</h2><p>Each algorithm is standardized to the same pooled distance mix. A reversal of the raw comparison indicates composition-driven aggregation bias, not proof of causal algorithm superiority.</p><p class="sub">Bootstrap resampling is stratified by version and distance category, with fixed pooled weights. This observational analysis does not control for unmeasured confounding factors such as geography, traffic, weather or dispatch timing.</p></div>
    </body></html>"""
    (OUT / "delivery_report.html").write_text(html, encoding="utf-8")

    reversal = (raw_diff < 0 < adjusted_diff) or (raw_diff > 0 > adjusted_diff)
    recommendation = ("Do not roll back solely on the raw KPI; confirm with a controlled evaluation."
                      if reversal else "Investigate further before changing the algorithm; composition adjustment alone is not conclusive.")
    memo = f"""# Dispatch algorithm investigation — decision memo

## Business question
Does the observed overall change in on-time delivery performance reflect algorithm performance or a different mix of delivery distances?

## Evidence
- Old raw on-time rate: {overall.loc['Old','rate']*100:.2f}% (n={overall.loc['Old','n']}).
- New raw on-time rate: {overall.loc['New','rate']*100:.2f}% (n={overall.loc['New','n']}).
- Raw New-minus-Old: {raw_diff*100:+.2f} percentage points.
- Old standardized on-time rate: {adjusted.loc['Old']*100:.2f}%.
- New standardized on-time rate: {adjusted.loc['New']*100:.2f}%.
- Adjusted New-minus-Old: {adjusted_diff*100:+.2f} percentage points.
- 95% stratified bootstrap percentile interval for adjusted difference: [{ci[0]*100:+.2f}, {ci[1]*100:+.2f}] percentage points ({BOOTSTRAP_REPS} replicates, seed {RANDOM_SEED}).
- Raw-versus-adjusted ranking reversal observed: {'Yes' if reversal else 'No'}.

## Method
We compared raw proportions and then directly standardized each algorithm's three distance-category rates to the same pooled distance-category distribution. A stratified bootstrap resampled observed deliveries within the six algorithm-by-distance groups while holding weights fixed.

## Recommendation
{recommendation}

## Limitations
This synthetic dataset is observational. Differences in traffic, geography, staffing, dispatch time and other factors are not controlled. Standardization is descriptive and does not prove causality. The bootstrap interval captures sampling uncertainty under the resampling assumptions, not all potential bias.

## Verification
Check counts against SQL, confirm segment sample sizes total the input row count, ensure pooled weights sum to one, and reconcile numbers across the CSV and HTML report.
"""
    (OUT / "investigation_summary.md").write_text(memo, encoding="utf-8")


def run():
    df = load_data()
    validate(df)
    overall, segments, weights, adjusted, raw_diff, adjusted_diff = summarize(df)
    ci = bootstrap_adjusted_diff(df, weights)
    write_outputs(overall, segments, weights, adjusted, raw_diff, adjusted_diff, ci)
    print(f"Rows loaded: {len(df)}")
    print("\nRaw overall rates:\n", (overall.assign(rate_pct=overall.rate * 100)).to_string())
    print("\nPooled weights:\n", weights.to_string())
    print("\nAdjusted rates (%):\n", (adjusted * 100).to_string())
    print(f"\nRaw New − Old: {raw_diff*100:+.2f} pp")
    print(f"Adjusted New − Old: {adjusted_diff*100:+.2f} pp")
    print(f"95% bootstrap CI: [{ci[0]*100:+.2f}, {ci[1]*100:+.2f}] pp")
    print(f"\nCreated outputs in {OUT}")


if __name__ == "__main__":
    run()
