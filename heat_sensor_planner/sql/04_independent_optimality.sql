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
