-- Run each query in DBeaver and interpret results during the recording.
-- 1. Source row counts and constraints
SELECT COUNT(*) AS total_deliveries,
       COUNT(DISTINCT delivery_id) AS distinct_ids,
       SUM(CASE WHEN on_time NOT IN (0, 1) THEN 1 ELSE 0 END) AS invalid_flags
FROM deliveries;

-- TODO 2: overall on-time rate by algorithm_version
-- Hint: COUNT(*) AS n, ROUND(100.0 * AVG(on_time), 2) AS on_time_pct

-- TODO 3: rate by algorithm_version and distance_category

-- TODO 4: distance mix (% of each algorithm's deliveries in each segment)

-- TODO 5: inspect if delivery_minutes agrees with promised_minutes and on_time
