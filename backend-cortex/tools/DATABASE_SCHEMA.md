# LifeOS - AI Memory Database Schema

## 🎯 核心概念
**這是 AI 的記憶資料庫** - 所有資料表都是為了讓 AI 能夠記憶、查詢、學習而設計。

---

## 📊 核心資料表

### 1. memories (每日記憶)
**用途**: AI 的短期記憶，每日記錄

```sql
CREATE TABLE memories (
  id UUID PRIMARY KEY,
  date DATE UNIQUE,              -- 一天一筆
  local_path TEXT,               -- 本地完整檔案路徑
  content_hash TEXT,             -- 內容雜湊值
  ai_insights TEXT,              -- AI 精簡版（向量友善）
  embedding VECTOR(3072),        -- 向量搜尋
  mood INT,
  focus INT,
  energy INT,
  tags TEXT[],
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**AI 查詢範例**:
- "2月17日我做了什麼？" → `SELECT * FROM memories WHERE date = '2026-02-17'`
- "最近關於 RAG 的記憶" → `SELECT * FROM memories WHERE 'RAG' = ANY(tags)`

---

### 2. MonthlyReview (月度總結)
**用途**: AI 的長期記憶，每月總結

```sql
CREATE TABLE MonthlyReview (
  id UUID PRIMARY KEY,
  year INT,
  month INT,
  summary TEXT,                  -- AI 整理的完整月總結
  key_achievements TEXT[],       -- 關鍵成就
  lessons_learned TEXT[],        -- 學到的教訓
  next_month_focus TEXT,         -- 下個月重點
  mood_avg FLOAT,
  focus_avg FLOAT,
  energy_avg FLOAT,
  created_at TIMESTAMP,
  UNIQUE(year, month)
);
```

**AI 查詢範例**:
- "2月整體表現如何？" → `SELECT * FROM MonthlyReview WHERE year=2026 AND month=2`
- "3月的目標是什麼？" → `SELECT next_month_focus FROM MonthlyReview WHERE year=2026 AND month=2`

---

### 3. nodes (知識節點)
**用途**: AI 的知識圖譜節點

```sql
CREATE TABLE nodes (
  id UUID PRIMARY KEY,
  type TEXT,                     -- concept, person, project, tool
  name TEXT,
  description TEXT,
  metadata JSONB,
  created_at TIMESTAMP
);
```

**範例節點**:
- `{type: "concept", name: "RAG", description: "Retrieval-Augmented Generation"}`
- `{type: "tool", name: "Supabase", description: "PostgreSQL database"}`

---

### 4. edges (知識關聯)
**用途**: AI 的知識圖譜連線

```sql
CREATE TABLE edges (
  id UUID PRIMARY KEY,
  source_id UUID REFERENCES nodes(id),
  target_id UUID REFERENCES nodes(id),
  relation_type TEXT,            -- uses, implements, relates_to
  strength FLOAT,
  created_at TIMESTAMP
);
```

**範例關聯**:
- `RAG --[implements]--> embedder.py`
- `LifeOS --[uses]--> Supabase`

---

### 5. tasks (任務清單)
**用途**: AI 追蹤任務進度

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  title TEXT,
  description TEXT,
  status TEXT,                   -- todo, in_progress, done
  priority INT,
  project_id UUID REFERENCES projects(id),
  due_date DATE,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

---

### 6. projects (專案管理)
**用途**: AI 追蹤專案狀態

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name TEXT,
  description TEXT,
  status TEXT,                   -- active, paused, completed
  progress FLOAT,                -- 0-100
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

---

### 7. cortex_growth_logs (AI 成長日誌)
**用途**: 記錄 AI 的學習和成長

```sql
CREATE TABLE cortex_growth_logs (
  id UUID PRIMARY KEY,
  event_type TEXT,               -- learned, improved, error
  description TEXT,
  metadata JSONB,
  created_at TIMESTAMP
);
```

---

### 8. system_usage (系統使用統計)
**用途**: 追蹤系統使用情況

```sql
CREATE TABLE system_usage (
  id UUID PRIMARY KEY,
  action TEXT,
  user_id TEXT,
  metadata JSONB,
  created_at TIMESTAMP
);
```

---

## ❌ 待刪除（重複或無用）

### LogEntry
**原因**: 與 `memories` 功能重複
**建議**: 刪除，統一使用 `memories`

### Task (大寫)
**原因**: 與 `tasks` (小寫) 重複
**建議**: 刪除，統一使用 `tasks`

### documents
**原因**: 用途不明，可能與 `memories` 或 `nodes` 重複
**建議**: 確認用途後決定是否刪除

---

## 🔄 AI 查詢模式

### 日常查詢
```sql
-- 今天做了什麼
SELECT ai_insights FROM memories WHERE date = CURRENT_DATE;

-- 本月進度
SELECT * FROM tasks WHERE status = 'in_progress';
```

### 知識查詢
```sql
-- RAG 相關知識
SELECT n.* FROM nodes n
JOIN edges e ON n.id = e.source_id OR n.id = e.target_id
WHERE n.name ILIKE '%RAG%';
```

### 長期記憶
```sql
-- 過去 3 個月的成長
SELECT * FROM MonthlyReview 
WHERE year = 2026 AND month >= 1 AND month <= 3
ORDER BY year, month;
```

---

## 🎯 設計原則

1. **一切為了 AI 查詢** - 資料結構優化給 AI 使用
2. **向量搜尋優先** - `memories` 表支援語意搜尋
3. **時間軸清晰** - 日 → 月 → 年的記憶層級
4. **知識圖譜** - nodes + edges 建立知識關聯
5. **進度追蹤** - tasks + projects 追蹤執行狀態

---

**最後更新**: 2026-02-17  
**維護者**: AI Cortex
