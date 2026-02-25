-- LifeOS v3.5 - Daily Memory Unique Constraint
-- Purpose: Ensure one memory per day (date as unique key)
-- Date: 2026-02-17

-- Add unique constraint on date column
-- This allows upsert operations to work correctly
DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'memories_date_unique'
    ) THEN
        ALTER TABLE memories ADD CONSTRAINT memories_date_unique UNIQUE (date);
    END IF;
END $$;

-- Add comment
COMMENT ON CONSTRAINT memories_date_unique ON memories IS 'Ensures one memory per day for append-mode operation';
