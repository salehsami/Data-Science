-- GHOST CUSTOMERS: SQL investigation. Complete and execute during the approved task.
-- 1. Preflight source counts (safe to test before recording)
SELECT (SELECT COUNT(*) FROM accounts) AS accounts,
       (SELECT COUNT(*) FROM events) AS events,
       (SELECT COUNT(DISTINCT session_id) FROM events) AS sessions;

-- TODO 2: Check duplicate event IDs and missing essential fields.
-- Hint: COUNT(*), COUNT(DISTINCT event_id), SUM(CASE WHEN ... IS NULL ...)

-- TODO 3: Show event volume by day to inspect spikes.
-- Hint: DATE(event_ts), COUNT(*), GROUP BY 1

-- TODO 4: Find sessions with the most events.
-- Hint: GROUP BY session_id, ORDER BY COUNT(*) DESC LIMIT 15

-- TODO 5: Find events-per-minute and session duration per session.
-- SQLite: julianday(MAX(event_ts)) - julianday(MIN(event_ts))

-- TODO 6: Show percentage of events accounted for by the top 5% busiest sessions.
-- Document chosen definition of top 5% and ties.
