-- LifeOS v3.5 Full Schema Definition
-- Date: 2026-02-14
-- Description: The "Genetic Code" of the system, defining Memory, Growth, and Structure.

-- 1. 基礎擴充
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Cortex 演化日誌 (玻璃盒核心)
-- Tracks AI decision process and architectural evolution
CREATE TABLE IF NOT EXISTS cortex_growth_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_context TEXT NOT NULL,
    options_provided JSONB NOT NULL,
    user_choice TEXT NOT NULL,
    ai_prediction TEXT,
    prediction_match BOOLEAN,
    lessons_learned TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 核心記憶 (Memories)
-- The primary storage for user thoughts and logs
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    date DATE NOT NULL UNIQUE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    mood INT DEFAULT 5 CHECK (mood >= 0 AND mood <= 10),
    focus INT DEFAULT 5 CHECK (focus >= 0 AND focus <= 10),
    energy INT DEFAULT 5 CHECK (energy >= 0 AND energy <= 10),
    tags TEXT[] NOT NULL DEFAULT '{}',
    category TEXT DEFAULT 'Life',
    is_ai BOOLEAN NOT NULL DEFAULT FALSE,
    ai_model TEXT,
    embedding VECTOR(768)
);

-- 4. 專案管理 (Projects)
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'on_hold', 'archived')),
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    start_date DATE,
    due_date DATE,
    parent_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 任務清單 (Tasks)
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    status TEXT DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'done')),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    source_memory_id UUID REFERENCES memories(id) ON DELETE SET NULL,
    due_date DATE,
    priority INT DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. 知識圖譜 (Nodes & Edges)
CREATE TABLE IF NOT EXISTS nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL UNIQUE,
    type TEXT DEFAULT 'concept' CHECK (type IN ('concept', 'tag', 'person', 'tool', 'project')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    relation TEXT DEFAULT 'related',
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_id, target_id, relation)
);

-- 7. 系統量測 (System Usage)
CREATE TABLE IF NOT EXISTS system_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE DEFAULT CURRENT_DATE,
    request_count INT DEFAULT 0,
    token_usage INT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. 索引建立
CREATE INDEX IF NOT EXISTS idx_memories_date ON memories (date DESC);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects (status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);

-- 9. 自動化更新時間之 Function 與 Trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_memories_updated_at ON memories;
CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- 10. 啟用 RLS 並設定全開策略（開發用）
ALTER TABLE cortex_growth_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_usage ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all access" ON cortex_growth_logs;
CREATE POLICY "Allow all access" ON cortex_growth_logs FOR ALL USING (TRUE) WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Allow all access" ON memories;
CREATE POLICY "Allow all access" ON memories FOR ALL USING (TRUE) WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Allow all access" ON projects;
CREATE POLICY "Allow all access" ON projects FOR ALL USING (TRUE) WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Allow all access" ON tasks;
CREATE POLICY "Allow all access" ON tasks FOR ALL USING (TRUE) WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Allow all access" ON nodes;
CREATE POLICY "Allow all access" ON nodes FOR ALL USING (TRUE) WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Allow all access" ON edges;
CREATE POLICY "Allow all access" ON edges FOR ALL USING (TRUE) WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Allow all access" ON system_usage;
CREATE POLICY "Allow all access" ON system_usage FOR ALL USING (TRUE) WITH CHECK (TRUE);
