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
