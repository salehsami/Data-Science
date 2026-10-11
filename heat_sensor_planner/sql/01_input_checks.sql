-- Run statements one at a time in DBeaver. These checks do not select a deployment.
-- Expected input sizes: 12 sites, 36 zones.
SELECT 'candidate_sites' AS dataset, COUNT(*) AS rows FROM candidate_sites
UNION ALL SELECT 'demand_zones', COUNT(*) FROM demand_zones;

-- These must return no rows.
SELECT site_id, COUNT(*) AS occurrences FROM candidate_sites GROUP BY site_id HAVING COUNT(*) <> 1;
SELECT zone_id, COUNT(*) AS occurrences FROM demand_zones GROUP BY zone_id HAVING COUNT(*) <> 1;
SELECT * FROM candidate_sites WHERE site_id IS NULL OR x_m IS NULL OR y_m IS NULL OR cost_eur IS NULL OR cost_eur <= 0 OR typeof(cost_eur) <> 'integer';
SELECT * FROM demand_zones WHERE zone_id IS NULL OR x_m IS NULL OR y_m IS NULL OR priority_population IS NULL OR priority_population < 0 OR typeof(priority_population) <> 'integer';

-- Inspect coordinate bounds and source population; fictional local grid, metres.
SELECT MIN(x_m) AS min_x, MAX(x_m) AS max_x, MIN(y_m) AS min_y, MAX(y_m) AS max_y FROM candidate_sites;
SELECT MIN(x_m) AS min_x, MAX(x_m) AS max_x, MIN(y_m) AS min_y, MAX(y_m) AS max_y, SUM(priority_population) AS total_population FROM demand_zones;
SELECT * FROM candidate_sites ORDER BY cost_eur, site_id;
SELECT * FROM demand_zones ORDER BY priority_population DESC, zone_id;
PRAGMA integrity_check;
PRAGMA foreign_key_check;
