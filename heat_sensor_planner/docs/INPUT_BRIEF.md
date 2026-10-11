# Fictional client brief and input provenance

Role: data scientist advising a municipal environmental-planning team.
Stakeholder: pilot coordinator choosing a small set of eligible installation sites.

## Objective agreed before analysis
Maximize the sum of priority-population counts in covered demand zones at a **300-metre planning radius**, using at most four sensors and at most **€1,000** in installation costs. A zone is covered if its centroid is within the radius of at least one selected site. Count its population once, even when several sites cover it.

Tie rules, in order: greater covered population; lower cost; fewer sensors; lexicographically smaller sorted site identifiers. Evaluate sensitivity at 200 and 400 metres for the **same selected sites**. These sensitivity rows do not change the primary objective or retune the deployment.

## Input tables
- `candidate_sites`: 12 eligible sites; `site_id`, local `x_m`, `y_m`, and integer `cost_eur`.
- `demand_zones`: 36 zone centroids; `zone_id`, local `x_m`, `y_m`, and integer `priority_population`.
- Coordinates are in a fictional planar grid in metres; they are not latitude/longitude.
- Priority-population values are counts assigned to each mutually exclusive zone. They are not weights to multiply again.
- All candidates are assumed accessible. No additional fairness or geographical quotas were requested.

## Provenance
All input records and application code were AI-generated before recording. `prepare_data.py` uses a fixed Python random seed for the zone counts, with predetermined site coordinates and costs. No external dataset, maps, copyrighted imagery, personal data, account or API is required. CSV copies of both input tables are included.

Synthetic counts vary across the grid to permit meaningful tradeoffs. This does not establish any real heat-risk relationship. Input generation does not optimize sites or complete a recommendation.

## Expected outputs created during recording
1. `outputs/selected_sites.csv` — chosen site rows.
2. `outputs/zone_coverage.csv` — every zone, covered status and contributing site IDs.
3. `outputs/feasible_combinations.csv` — all feasible combinations, ranked under the chosen radius.
4. `outputs/fixed_deployment_sensitivity.csv` — same chosen sites, three radii.
5. `outputs/analysis_summary.json` — constraints, metrics and comparison with the optimum.
6. `outputs/Deployment_Recommendation.md` — analyst-written recommendation and limitations.

The application writes the chosen selection and coverage into analysis tables in SQLite when Save analysis files is clicked. These tables are empty in the starter database.
