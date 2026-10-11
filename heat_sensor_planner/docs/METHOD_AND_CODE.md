# Method and code explained

## Coverage and population
For a site and zone, calculate squared distance: `(site_x-zone_x)^2 + (site_y-zone_y)^2`. Compare with `radius^2`; no square root is required. A point exactly at the radius is included. Because coordinates use a small local metre grid, planar distance is the stated model.

`covers()` tests a single pair. `evaluate()` uses `any()` to ask whether any selected site covers a zone. It then sums each qualifying zone's population once. This prevents overlap inflation.

## Exact optimization
`itertools.combinations` produces subsets without repeated sites. For 12 candidates and sizes 0,1,2,3,4, there are 1+12+66+220+495 = **794** subsets. Including zero sites makes the optimization definition complete.

`optimize()` evaluates all these subsets, retains those satisfying the installation budget, and sorts them using `rank_key()`. Its tuple contains negative covered population (so the highest is first), cost, site count and ordered IDs. The first row is the exact optimum for the stated finite candidate set and coverage assumptions. It is not a proof of real-world environmental representativeness.

## Sensitivity
`evaluate()` is called for the same site IDs at 200, 300 and 400 m. Changing the radius selector and optimizing again is a different analysis. For the approved task, optimize at 300 m and use the fixed-deployment table for sensitivity. Covered population cannot fall when radius increases for a fixed selection and nonnegative populations.

## Source and exports
`prepare_data.py` creates only source records and empty analysis tables. It never calls the optimizer. The seed makes input populations repeatable.

`server.py` hosts the tool only at 127.0.0.1:8765. Loading the page retrieves inputs and evaluates the empty selection, but does not run the optimization or write outputs. Searching computes results in memory. Saving writes CSV/JSON exports and updates SQLite tables in a transaction.

`analysis_summary.json` contains computed evidence, including whether the saved selection matches the optimum. It deliberately contains no analyst recommendation. Complete that judgment in the memo.

## Independent checks
The SQL coverage check uses EXISTS against source zones and selected sites, rather than trusting the exported covered flag. The optional SQL optimum query uses bit masks to enumerate all possible subsets, filters constraints and reconstructs each combination's union coverage. Its top results should match the Python optimizer at 300 m. The tie rule uses canonical fixed-width site IDs, making alphabetical ordering deterministic.

## Assumptions
Centroid inclusion represents an entire zone by a single point; all sites are eligible; costs are installation only; priority population is the sole optimization objective; no fairness quota, terrain barrier, outage risk or scientific heat-representativeness criterion is modeled. Additional constraints could change the decision and require a revised task scope.
