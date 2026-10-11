-- Read-only investigation queries for the recorded task.
SELECT id, display_name FROM agents ORDER BY id;
SELECT id, owner_agent_id, segment FROM customers ORDER BY id;
SELECT a.id AS agent_id, a.display_name, c.id AS customer_id
FROM agents a JOIN customers c ON c.owner_agent_id = a.id
ORDER BY a.id, c.id;
-- Suggested additional query to implement during recorded workflow:
-- check for orphaned customer ownership records.
