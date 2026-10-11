-- GHOST CUSTOMERS: SQL investigation. Complete and execute during the approved task.
-- 1. Preflight source counts (safe to test before recording)
SELECT (SELECT COUNT(*) FROM accounts) AS accounts,
       (SELECT COUNT(*) FROM events) AS events,
       (SELECT COUNT(DISTINCT session_id) FROM events) AS sessions;

-- TODO 2: Check duplicate event IDs and missing essential fields.
-- Hint: COUNT(*), COUNT(DISTINCT event_id), SUM(CASE WHEN ... IS NULL ...)
SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT event_id) AS unique_event_ids,
    SUM(CASE
        WHEN event_id IS NULL
          OR account_id IS NULL
          OR session_id IS NULL
          OR event_ts IS NULL
          OR event_type IS NULL
          OR page IS NULL
        THEN 1 ELSE 0
    END) AS missing_required_fields
FROM events;

-- TODO 3: Show event volume by day to inspect spikes.
-- Hint: DATE(event_ts), COUNT(*), GROUP BY 1
SELECT
    DATE(event_ts) AS activity_date,
    COUNT(*) AS total_events,
    COUNT(DISTINCT session_id) AS active_sessions
FROM events
GROUP BY DATE(event_ts)
ORDER BY activity_date;


-- TODO 4: Find sessions with the most events.
-- Hint: GROUP BY session_id, ORDER BY COUNT(*) DESC LIMIT 15
SELECT
    session_id,
    account_id,
    COUNT(*) AS event_count
FROM events
GROUP BY session_id, account_id
ORDER BY event_count DESC
LIMIT 15;

-- TODO 5: Find events-per-minute and session duration per session.
-- SQLite: julianday(MAX(event_ts)) - julianday(MIN(event_ts))
SELECT
    session_id,
    COUNT(*) AS event_count,
    ROUND(
        (julianday(MAX(event_ts)) -
         julianday(MIN(event_ts))) * 86400,
        2
    ) AS duration_sec,
    ROUND(
        COUNT(*) * 60.0 /
        NULLIF(
            (julianday(MAX(event_ts)) -
             julianday(MIN(event_ts))) * 86400,
            0
        ),
        2
    ) AS events_per_min
FROM events
GROUP BY session_id
ORDER BY events_per_min DESC;


-- TODO 6: Show percentage of events accounted for by the top 5% busiest sessions.
-- Document chosen definition of top 5% and ties.
WITH session_counts AS (
    SELECT
        session_id,
        COUNT(*) AS event_count
    FROM events
    GROUP BY session_id
),
ranked AS (
    SELECT
        event_count,
        ROW_NUMBER() OVER (
            ORDER BY event_count DESC, session_id
        ) AS rank_no
    FROM session_counts
)
SELECT
    SUM(CASE WHEN rank_no <= 32
        THEN event_count ELSE 0 END)
        AS top_5pct_events,
    SUM(event_count) AS total_events,
    ROUND(
        100.0 * SUM(CASE WHEN rank_no <= 32
            THEN event_count ELSE 0 END)
        / SUM(event_count),
        2
    ) AS top_5pct_event_share
FROM ranked;