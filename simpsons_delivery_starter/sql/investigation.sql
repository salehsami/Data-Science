-- HEAT SENSOR PLANNER: COMPLETE INVESTIGATION
-- SQLite / DBeaver. Read-only queries; no data is changed.
-- Execute ONE statement at a time, inspecting its result before continuing.
-- Phase 1: before selecting a deployment.
-- Phases 2 and 3: AFTER Save analysis files in Firefox; refresh DBeaver.
-- Phase 4: independent primary-radius optimum verification (300 metres).
-- Do not run the whole page against the empty starter and treat it as validation.

-- PHASE 1: AUDIT THE SYNTHETIC INPUTS

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

-- PHASE 2: VERIFY THE SAVED DEPLOYMENT

-- Prerequisite: all three settings must exist and match the approved objective.
-- Expected: READY. Otherwise return to Firefox and save the final 300 m selection.
SELECT CASE WHEN
 (SELECT COUNT(*) FROM selected_sites) BETWEEN 1 AND 4
 AND (SELECT COUNT(*) FROM zone_coverage)=36
 AND (SELECT value FROM analysis_settings WHERE key='radius_m')='300'
 AND (SELECT value FROM analysis_settings WHERE key='budget_eur')='1000'
 AND (SELECT value FROM analysis_settings WHERE key='max_sites')='4'
 THEN 'READY' ELSE 'NOT READY: save the primary deployment first' END AS analysis_readiness;

-- Run after clicking Save analysis files in Firefox. Refresh/reconnect DBeaver.
-- Counts must be >0. Empty analysis tables mean there is no saved selection yet.
SELECT * FROM analysis_settings;
SELECT * FROM selected_sites ORDER BY site_id;
SELECT COUNT(*) AS selected_count, SUM(cost_eur) AS total_cost_eur,
       CASE WHEN COUNT(*) BETWEEN 1 AND 4 AND SUM(cost_eur) <= 1000 THEN 'PASS' ELSE 'FAIL' END AS constraints
FROM selected_sites;

-- No unknown or altered site rows allowed: must return no rows.
SELECT s.* FROM selected_sites s LEFT JOIN candidate_sites c ON c.site_id=s.site_id
WHERE c.site_id IS NULL OR s.x_m<>c.x_m OR s.y_m<>c.y_m OR s.cost_eur<>c.cost_eur;

-- Independently reconstruct coverage with EXISTS, preventing overlap double counting.
WITH independently_covered AS (
 SELECT z.*, CASE WHEN EXISTS (
   SELECT 1 FROM selected_sites s
   WHERE (s.x_m-z.x_m)*(s.x_m-z.x_m)+(s.y_m-z.y_m)*(s.y_m-z.y_m)
      <= (SELECT CAST(value AS INTEGER)*CAST(value AS INTEGER) FROM analysis_settings WHERE key='radius_m')
 ) THEN 1 ELSE 0 END AS covered
 FROM demand_zones z
)
SELECT SUM(covered) AS covered_zones,
 SUM(CASE WHEN covered=1 THEN priority_population ELSE 0 END) AS covered_population,
 SUM(priority_population) AS total_population,
 ROUND(100.0*SUM(CASE WHEN covered=1 THEN priority_population ELSE 0 END)/NULLIF(SUM(priority_population),0),2) AS coverage_pct
FROM independently_covered;

-- Exported coverage summary must match the independent reconstruction above.
SELECT COUNT(*) AS exported_zones, SUM(covered) AS covered_zones,
 SUM(CASE WHEN covered=1 THEN priority_population ELSE 0 END) AS covered_population FROM zone_coverage;

-- Exact per-zone comparison: must return no rows.
SELECT z.zone_id FROM demand_zones z LEFT JOIN zone_coverage v ON v.zone_id=z.zone_id
WHERE v.zone_id IS NULL OR v.priority_population<>z.priority_population OR v.x_m<>z.x_m OR v.y_m<>z.y_m
OR v.covered <> CASE WHEN EXISTS (
 SELECT 1 FROM selected_sites s
 WHERE (s.x_m-z.x_m)*(s.x_m-z.x_m)+(s.y_m-z.y_m)*(s.y_m-z.y_m)
 <= (SELECT CAST(value AS INTEGER)*CAST(value AS INTEGER) FROM analysis_settings WHERE key='radius_m')
) THEN 1 ELSE 0 END;
SELECT v.zone_id FROM zone_coverage v LEFT JOIN demand_zones z ON z.zone_id=v.zone_id WHERE z.zone_id IS NULL;

-- Uncovered zones and overlaps explain practical tradeoffs.
SELECT * FROM zone_coverage WHERE covered=0 ORDER BY priority_population DESC,zone_id;
SELECT z.zone_id,z.priority_population,COUNT(s.site_id) AS covering_site_count
FROM demand_zones z JOIN selected_sites s
ON (s.x_m-z.x_m)*(s.x_m-z.x_m)+(s.y_m-z.y_m)*(s.y_m-z.y_m)
 <= (SELECT CAST(value AS INTEGER)*CAST(value AS INTEGER) FROM analysis_settings WHERE key='radius_m')
GROUP BY z.zone_id HAVING COUNT(s.site_id)>1 ORDER BY covering_site_count DESC,z.zone_id;

-- PHASE 3: FIXED-DEPLOYMENT RADIUS SENSITIVITY

-- The selected deployment remains fixed. Coverage must not fall as radius grows.
WITH radii(radius_m) AS (VALUES(200),(300),(400)),
checks AS (
 SELECT r.radius_m,z.zone_id,z.priority_population,
 CASE WHEN EXISTS(SELECT 1 FROM selected_sites s
 WHERE (s.x_m-z.x_m)*(s.x_m-z.x_m)+(s.y_m-z.y_m)*(s.y_m-z.y_m)<=r.radius_m*r.radius_m)
 THEN 1 ELSE 0 END AS covered
 FROM radii r CROSS JOIN demand_zones z
)
SELECT radius_m,SUM(covered) AS covered_zones,
 SUM(CASE WHEN covered=1 THEN priority_population ELSE 0 END) AS covered_population,
 ROUND(100.0*SUM(CASE WHEN covered=1 THEN priority_population ELSE 0 END)/NULLIF(SUM(priority_population),0),2) AS coverage_pct
FROM checks GROUP BY radius_m ORDER BY radius_m;

-- PHASE 4: INDEPENDENT EXACT OPTIMALITY CHECK

-- Optional stronger verification: enumerate all 2^12 masks in SQLite,
-- restrict to <=4 sites and <=1000 EUR; independently rebuild covered population.
-- Fixed to the primary approved radius: 300 metres.
WITH RECURSIVE
numbered AS (SELECT *, ROW_NUMBER() OVER (ORDER BY site_id)-1 AS bit_no FROM candidate_sites),
masks(mask) AS (SELECT 0 UNION ALL SELECT mask+1 FROM masks WHERE mask+1 < (1 << (SELECT COUNT(*) FROM candidate_sites))),
deployments AS (
 SELECT m.mask,COUNT(s.site_id) AS site_count,COALESCE(SUM(s.cost_eur),0) AS cost_eur
 FROM masks m LEFT JOIN numbered s ON (m.mask & (1 << s.bit_no))<>0
 GROUP BY m.mask HAVING COUNT(s.site_id)<=4 AND COALESCE(SUM(s.cost_eur),0)<=1000
),
scored AS (
 SELECT d.*,COALESCE((SELECT SUM(z.priority_population) FROM demand_zones z WHERE EXISTS(
 SELECT 1 FROM numbered s WHERE (d.mask & (1 << s.bit_no))<>0
 AND (s.x_m-z.x_m)*(s.x_m-z.x_m)+(s.y_m-z.y_m)*(s.y_m-z.y_m)<=300*300)),0) AS covered_population,
 COALESCE((SELECT GROUP_CONCAT(site_id,';') FROM (SELECT s.site_id FROM numbered s WHERE (d.mask & (1 << s.bit_no))<>0 ORDER BY s.site_id)),'') AS site_ids
 FROM deployments d
)
SELECT site_ids,site_count,cost_eur,covered_population FROM scored
ORDER BY covered_population DESC,cost_eur,site_count,site_ids LIMIT 10;
