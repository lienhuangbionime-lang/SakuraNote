-- LifeOS Database Cleanup
-- Purpose: Remove redundant tables
-- Date: 2026-02-17

-- 1. Drop LogEntry (redundant with memories)
DROP TABLE IF EXISTS "LogEntry" CASCADE;

-- 2. Drop Task (redundant with tasks)
DROP TABLE IF EXISTS "Task" CASCADE;

-- 3. Drop documents (if confirmed unused)
-- Uncomment after confirming usage
-- DROP TABLE IF EXISTS documents CASCADE;

-- Add comments to core tables
COMMENT ON TABLE memories IS 'AI daily memory with vector search capability';
COMMENT ON TABLE "MonthlyReview" IS 'AI monthly reflection and goals';
COMMENT ON TABLE nodes IS 'Knowledge graph nodes';
COMMENT ON TABLE edges IS 'Knowledge graph relationships';
COMMENT ON TABLE tasks IS 'Task tracking for AI';
COMMENT ON TABLE projects IS 'Project management for AI';
COMMENT ON TABLE cortex_growth_logs IS 'AI learning and growth logs';
COMMENT ON TABLE system_usage IS 'System usage statistics';
