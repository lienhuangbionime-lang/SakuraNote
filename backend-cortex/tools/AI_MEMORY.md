# LifeOS v3.5 - AI Development Memory

## 🎯 核心架構決策

### 本地優先 (Local-First)
- **完整記憶**: `data/memories/YYYY-MM-DD.json`
- **Supabase**: 僅存 AI 見解 + embedding + 索引
- **原因**: 資料主權、離線可用、成本低

### 一天一筆記憶 (Append Mode)
- 同一天多次寫入 → 追加到 `entries[]` 陣列
- `combined_content` 自動合併所有內容
- Supabase 使用 `upsert(on_conflict="date")`

### RAG 架構
- **embedder.py**: 3072-dim vectors (text-embedding-004)
- **rag.py**: 混合搜尋（語意 + 篩選）
- **chat.py**: 自動注入相關記憶到 prompt

---

## 📋 已知問題與解決方案

### 1. Supabase RPC Function 缺失
**問題**: `match_memories()` 函數未定義
**解決**: 執行 `migrations/006_match_memories_rpc.sql`

### 2. Unicode 編碼錯誤 (Windows)
**問題**: `charmap` 無法處理特殊字元
**解決**: 所有檔案 I/O 使用 `encoding="utf-8"`

### 3. Unique Constraint 重複執行
**問題**: `memories_date_unique` 已存在
**解決**: 正常，代表已執行過，可忽略

---

## 🗂️ 核心檔案清單

### 必須檔案
1. **`.cursorrules`** - AI 開發規則
2. **`evolution_log.json`** - 系統演化歷史
3. **`soul_manager.py`** - 靈魂管理器
4. **`SYSTEM_CONTEXT.md`** - 系統架構文檔
5. **`task.md`** - 當前任務狀態

### 關鍵程式碼
- `app/services/embedder.py` - 向量生成
- `app/services/rag.py` - 混合搜尋
- `app/api/v1/ingest.py` - 記憶寫入（append mode）
- `app/api/v1/chat.py` - RAG 記憶注入
- `tools/task_tracker.py` - 任務完成追蹤
- `tools/cortex_sync.py` - 雲端同步

---

## 🔄 開發工作流程

### Phase 1: RAG Infrastructure ✅
- 建立 `embedder.py` (3072-dim)
- 建立 `rag.py` (hybrid search)
- 修改 `ingest.py` 使用新 embedder

### Phase 2: Cognitive Awakening ✅
- 修改 `chat.py` 注入 RAG context
- 實作本地優先架構
- 實作 append mode

### Phase 3: Agentic Automation ⏳
- 建立 `daily_reflection.py`
- 整合 APScheduler 到 `main.py`

---

## 🚨 重要提醒

### 資料結構
```json
// data/memories/2026-02-17.json
{
  "id": "uuid",
  "date": "2026-02-17",
  "entries": [
    {
      "time": "ISO timestamp",
      "content": "原始輸入",
      "ai_processed": "AI 處理後",
      "metadata": {...}
    }
  ],
  "combined_content": "所有 content 合併",
  "created_at": "...",
  "updated_at": "..."
}
```

### Supabase Schema
```sql
-- 必須欄位
date (UNIQUE)
local_path
content_hash
ai_insights
embedding (vector 3072)
```

### 同步到雲端
```bash
python tools/cortex_sync.py
```

---

## 🎯 下一個 AI 開發者須知

1. **先讀**: `.cursorrules`, `evolution_log.json`, `SYSTEM_CONTEXT.md`
2. **理解**: 本地優先 + append mode 架構
3. **檢查**: `task.md` 看當前進度
4. **執行**: 缺少的 Supabase migrations
5. **測試**: `python tools/test_local_storage.py`

---

**最後更新**: 2026-02-17  
**狀態**: Phase 1 & 2 完成，Phase 3 待實作
