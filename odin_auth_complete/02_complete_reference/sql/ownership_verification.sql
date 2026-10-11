-- Open against the local synthetic support.db database in DBeaver.
-- 1. Verify owners exist and map to fictional agents.
SELECT c.id AS customer_id, c.owner_agent_id, a.display_name AS assigned_agent
FROM customers c LEFT JOIN agents a ON a.id = c.owner_agent_id
ORDER BY c.id;

-- 2. Look for customers referencing a nonexistent owner; expected zero rows.
SELECT c.id, c.owner_agent_id
FROM customers c LEFT JOIN agents a ON a.id = c.owner_agent_id
WHERE a.id IS NULL;

-- 3. Count customers per assigned agent; expected AG-001=2, AG-002=2.
SELECT owner_agent_id, COUNT(*) AS assigned_customers
FROM customers GROUP BY owner_agent_id ORDER BY owner_agent_id;

-- 4. Focus on cross-agent target owned by AG-002, not AG-001.
SELECT id, owner_agent_id FROM customers WHERE id = 'CUST-201';
