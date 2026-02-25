-- LifeOS v3.5 - Local-First Storage Schema Migration
-- Purpose: Add local file reference columns to memories table
-- Date: 2026-02-17

-- Add new columns for local-first architecture
ALTER TABLE memories ADD COLUMN IF NOT EXISTS local_path TEXT;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS content_hash TEXT;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS ai_insights TEXT;

-- Make content column nullable (for backward compatibility)
ALTER TABLE memories ALTER COLUMN content DROP NOT NULL;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_memories_local_path ON memories(local_path);
CREATE INDEX IF NOT EXISTS idx_memories_content_hash ON memories(content_hash);

-- Add comment
COMMENT ON COLUMN memories.local_path IS 'Relative path to local JSON file (e.g., 2026-02-17.json)';
COMMENT ON COLUMN memories.content_hash IS 'SHA256 hash of original content for integrity verification';
COMMENT ON COLUMN memories.ai_insights IS 'AI-processed summary/insights (stored in Supabase for quick access)';
COMMENT ON COLUMN memories.content IS 'DEPRECATED: Full content now stored locally. This column kept for backward compatibility.';
