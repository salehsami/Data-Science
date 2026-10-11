-- CLOCK OFFSET ANALYSIS: COMPLETE INVESTIGATION (SQLite / DBeaver)
-- Read-only. Execute ONE numbered statement at a time.
-- 01-11 before analysis. 12-24 AFTER Freeze offset and validate, then Save analysis files.
-- Correction: corrected B timestamp = original B timestamp + offset_seconds.
-- Pair A(t) with B(t - offset_seconds). Negative correction moves B earlier.
-- Query 16 uses estimation only. Do not choose a new offset after viewing validation.
-- Queries 16 and 20 use r-squared to avoid requiring a SQLite SQRT extension.
-- Signed r-squared in query 16 orders correlations correctly, even for negative r.

-- 01. Source reading counts
-- Expected: 480 per sensor
SELECT sensor_id,COUNT(*) AS reading_count FROM readings GROUP BY sensor_id ORDER BY sensor_id;

-- 02. Duplicate raw timestamps
-- Expected: no rows
SELECT sensor_id,recorded_at,COUNT(*) AS occurrences FROM readings GROUP BY sensor_id,recorded_at HAVING COUNT(*)>1;

-- 03. Required fields and sensor identifiers
-- Expected: no rows
SELECT * FROM readings WHERE sensor_id NOT IN ('A','B') OR sensor_id IS NULL OR t_seconds IS NULL OR recorded_at IS NULL OR temperature_c IS NULL;

-- 04. Numeric values and grid boundaries
-- Expected: no rows
SELECT * FROM readings WHERE typeof(t_seconds)<>'integer' OR typeof(temperature_c) NOT IN ('integer','real') OR t_seconds<0 OR t_seconds>=14400 OR t_seconds%30<>0;

-- 05. Raw timestamp conversion consistency
-- Expected: no rows
SELECT * FROM readings WHERE strftime('%s',recorded_at) IS NULL OR strftime('%s',recorded_at)-strftime('%s','2026-01-15T08:00:00Z')<>t_seconds;

-- 06. Sampling-gap audit
-- Expected: no rows
WITH sequence AS (SELECT sensor_id,t_seconds,LAG(t_seconds) OVER(PARTITION BY sensor_id ORDER BY t_seconds) AS previous_t FROM readings)
SELECT sensor_id,previous_t,t_seconds,t_seconds-previous_t AS gap_seconds FROM sequence WHERE previous_t IS NOT NULL AND t_seconds-previous_t<>30;

-- 07. Timestamp coverage and temperature range
SELECT sensor_id,MIN(recorded_at) AS first_timestamp,MAX(recorded_at) AS last_timestamp,MIN(temperature_c) AS min_c,MAX(temperature_c) AS max_c FROM readings GROUP BY sensor_id ORDER BY sensor_id;

-- 08. Raw timestamps present in only one sensor
-- Expected: no rows
SELECT a.t_seconds FROM readings a LEFT JOIN readings b ON b.sensor_id='B' AND b.t_seconds=a.t_seconds WHERE a.sensor_id='A' AND b.t_seconds IS NULL
UNION ALL SELECT b.t_seconds FROM readings b LEFT JOIN readings a ON a.sensor_id='A' AND a.t_seconds=b.t_seconds WHERE b.sensor_id='B' AND a.t_seconds IS NULL;

-- 09. Raw-window counts
-- Expected: 360 per sensor estimation; 120 per sensor validation
SELECT sensor_id,CASE WHEN t_seconds<10800 THEN 'estimation' ELSE 'validation' END AS phase,COUNT(*) AS reading_count FROM readings GROUP BY sensor_id,phase ORDER BY phase,sensor_id;

-- 10. Common interior reference counts
-- Expected: 320 estimation; 80 validation
SELECT 'estimation' AS phase,COUNT(*) AS reference_pairs FROM readings WHERE sensor_id='A' AND t_seconds>=600 AND t_seconds<10200
UNION ALL SELECT 'validation',COUNT(*) FROM readings WHERE sensor_id='A' AND t_seconds>=11400 AND t_seconds<13800;

-- 11. SQLite integrity
-- Expected: ok
PRAGMA integrity_check;

-- 12. Analysis readiness after export
-- Expected: READY after saving
SELECT CASE WHEN (SELECT COUNT(*) FROM candidate_scores)=41 AND (SELECT COUNT(*) FROM aligned_pairs)=400 AND (SELECT COUNT(*) FROM phase_metrics)=2 AND (SELECT value FROM analysis_settings WHERE key='validated')='1' THEN 'READY' ELSE 'NOT READY: validate and save in Firefox first' END AS readiness;

-- 13. Saved sign and settings
SELECT * FROM analysis_settings ORDER BY key;

-- 14. Candidate pair-count equality
-- Expected: 41 candidates; min=max=320
SELECT COUNT(*) AS candidates,MIN(pair_count) AS min_pairs,MAX(pair_count) AS max_pairs FROM candidate_scores;

-- 15. Saved candidate rankings
SELECT offset_seconds,pair_count,ROUND(correlation,6) AS correlation,ROUND(mae_c,6) AS mae_c,ROUND(bias_c,6) AS bias_c FROM candidate_scores ORDER BY correlation DESC,mae_c,ABS(offset_seconds),offset_seconds LIMIT 5;

-- 16. Independent estimation-only offset search
-- Expected: top offset agrees with dashboard; signed r-squared is not Pearson r
WITH RECURSIVE offsets(offset_seconds) AS (SELECT -600 UNION ALL SELECT offset_seconds+30 FROM offsets WHERE offset_seconds<600),
paired AS (
 SELECT o.offset_seconds,a.temperature_c AS x,b.temperature_c AS y
 FROM offsets o JOIN readings a ON a.sensor_id='A' AND a.t_seconds>=600 AND a.t_seconds<10200
 JOIN readings b ON b.sensor_id='B' AND b.t_seconds=a.t_seconds-o.offset_seconds
 WHERE b.t_seconds>=0 AND b.t_seconds<10800
), sums AS (
 SELECT offset_seconds,COUNT(*) AS n,SUM(x) AS sx,SUM(y) AS sy,SUM(x*x) AS sxx,SUM(y*y) AS syy,SUM(x*y) AS sxy,AVG(ABS(y-x)) AS mae_c,AVG(y-x) AS bias_c
 FROM paired GROUP BY offset_seconds
), scored AS (
 SELECT *,CASE WHEN n*sxy-sx*sy>=0 THEN 1.0 ELSE -1.0 END * (n*sxy-sx*sy)*(n*sxy-sx*sy)/NULLIF((n*sxx-sx*sx)*(n*syy-sy*sy),0) AS signed_correlation_squared FROM sums
)
SELECT offset_seconds,n AS pair_count,ROUND(signed_correlation_squared,6) AS signed_correlation_squared,ROUND(mae_c,6) AS mae_c,ROUND(bias_c,6) AS bias_c
FROM scored ORDER BY signed_correlation_squared DESC,mae_c,ABS(offset_seconds),offset_seconds LIMIT 5;

-- 17. Verify original B readings and correction sign
-- Expected: no rows
SELECT p.phase,p.reference_t_seconds FROM aligned_pairs p
LEFT JOIN readings a ON a.sensor_id='A' AND a.t_seconds=p.reference_t_seconds
LEFT JOIN readings b ON b.sensor_id='B' AND b.t_seconds=p.b_raw_t_seconds
WHERE a.sensor_id IS NULL OR b.sensor_id IS NULL OR p.a_temp_c<>a.temperature_c OR p.b_temp_c<>b.temperature_c OR p.reference_at<>a.recorded_at OR p.b_original_at<>b.recorded_at
OR p.b_raw_t_seconds+CAST((SELECT value FROM analysis_settings WHERE key='offset_seconds') AS INTEGER)<>p.reference_t_seconds
OR p.b_corrected_at<>p.reference_at;

-- 18. No cross-window pairs
-- Expected: no rows
SELECT * FROM aligned_pairs WHERE
(phase='estimation' AND (reference_t_seconds<600 OR reference_t_seconds>=10200 OR b_raw_t_seconds<0 OR b_raw_t_seconds>=10800))
OR (phase='validation' AND (reference_t_seconds<11400 OR reference_t_seconds>=13800 OR b_raw_t_seconds<10800 OR b_raw_t_seconds>=14400))
OR phase NOT IN ('estimation','validation');

-- 19. Concrete sign-convention examples
SELECT phase,reference_at,b_original_at,b_corrected_at,a_temp_c,b_temp_c FROM aligned_pairs WHERE reference_t_seconds IN (3600,12000) ORDER BY reference_t_seconds;

-- 20. Independent raw-source phase metrics
-- Expected: compare squared correlation with dashboard correlation-squared row
WITH reference AS (
 SELECT CASE WHEN t_seconds<10800 THEN 'estimation' ELSE 'validation' END AS phase,t_seconds,temperature_c AS x FROM readings
 WHERE sensor_id='A' AND ((t_seconds>=600 AND t_seconds<10200) OR (t_seconds>=11400 AND t_seconds<13800))
), modes(mode,offset_seconds) AS (SELECT 'baseline',0 UNION ALL SELECT 'aligned',CAST(value AS INTEGER) FROM analysis_settings WHERE key='offset_seconds'),
paired AS (SELECT r.phase,m.mode,r.x,b.temperature_c AS y FROM reference r CROSS JOIN modes m
JOIN readings b ON b.sensor_id='B' AND b.t_seconds=r.t_seconds-m.offset_seconds
WHERE (r.phase='estimation' AND b.t_seconds>=0 AND b.t_seconds<10800) OR (r.phase='validation' AND b.t_seconds>=10800 AND b.t_seconds<14400)),
sums AS (SELECT phase,mode,COUNT(*) AS n,SUM(x) AS sx,SUM(y) AS sy,SUM(x*x) AS sxx,SUM(y*y) AS syy,SUM(x*y) AS sxy,AVG(ABS(y-x)) AS mae_c,AVG(y-x) AS bias_c FROM paired GROUP BY phase,mode)
SELECT phase,mode,n AS pair_count,ROUND(mae_c,6) AS mae_c,ROUND(bias_c,6) AS bias_c,
ROUND((n*sxy-sx*sy)*(n*sxy-sx*sy)/NULLIF((n*sxx-sx*sx)*(n*syy-sy*sy),0),6) AS correlation_squared
FROM sums ORDER BY phase,mode;

-- 21. Saved phase metrics
SELECT phase,offset_seconds,pair_count,ROUND(baseline_correlation,6) AS original_r,ROUND(aligned_correlation,6) AS aligned_r,ROUND(baseline_mae_c,6) AS original_mae_c,ROUND(aligned_mae_c,6) AS aligned_mae_c,ROUND(aligned_bias_c,6) AS remaining_bias_c,ROUND(mae_reduction_pct,2) AS mae_reduction_pct FROM phase_metrics ORDER BY phase;

-- 22. Exported phase counts and difference checks
-- Expected: 320 estimation; 80 validation; metrics match source reconstruction
SELECT phase,COUNT(*) AS pair_count,ROUND(AVG(ABS(b_temp_c-a_temp_c)),6) AS aligned_mae_c,ROUND(AVG(b_temp_c-a_temp_c),6) AS aligned_bias_c FROM aligned_pairs GROUP BY phase ORDER BY phase;

-- 23. Detect altered baseline or difference fields
-- Expected: no rows
SELECT p.phase,p.reference_t_seconds FROM aligned_pairs p LEFT JOIN readings b ON b.sensor_id='B' AND b.t_seconds=p.reference_t_seconds
WHERE b.sensor_id IS NULL OR p.baseline_b_temp_c<>b.temperature_c OR ABS(p.b_minus_a_c-(p.b_temp_c-p.a_temp_c))>0.000000001 OR ABS(p.baseline_b_minus_a_c-(p.baseline_b_temp_c-p.a_temp_c))>0.000000001;

-- 24. Remaining raw input counts
-- Expected: 480 per sensor; raw inputs preserved
SELECT sensor_id,COUNT(*) AS reading_count FROM readings GROUP BY sensor_id ORDER BY sensor_id;

