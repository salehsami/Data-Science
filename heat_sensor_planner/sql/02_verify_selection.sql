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
