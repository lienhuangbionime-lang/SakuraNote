# 開發 AI 交接文檔

## 🎯 你是誰

你是**開發 AI**，負責開發 LifeOS 系統。

---

## 📋 系統架構

### 系統 AI（Runtime）
**位置**: `app/` + Supabase  
**職責**: 服務使用者，提供 API

```
app/api/v1/
├── ingest.py      # 接收日記
├── chat.py        # 對話
└── ...

app/services/
├── rag.py         # 記憶搜尋
├── embedder.py    # 向量生成
└── ...

Supabase:
├── memories       # 每日記憶
├── MonthlyReview  # 月度總結
└── ...
```

### 開發 AI（你）
**位置**: `tools/`  
**職責**: 開發系統，理解架構

```
tools/
├── AI_MEMORY.md           # 開發決策和已知問題
├── DATABASE_SCHEMA.md     # 資料庫結構
├── task.md                # 當前任務
├── ai_memory_reader.py    # 讀取記憶工具
└── ...
```

---

## 🚀 立刻開始

### 1. 先讀這 3 個檔案（5 分鐘）
```bash
tools/AI_MEMORY.md         # 核心決策
tools/DATABASE_SCHEMA.md   # 資料結構
tools/task.md              # 當前進度
```

### 2. 理解核心概念
- **本地優先**: 完整記憶在 `data/memories/YYYY-MM-DD.json`
- **Supabase**: 只存 AI 精簡版 + embedding
- **一天一筆**: 同一天多次寫入會追加（append mode）

### 3. 查看當前狀態
```python
# 使用工具查詢
python tools/ai_memory_reader.py
```

---

## 📊 資料流程

### 日記寫入
```
使用者輸入
    ↓
ingest.py (AI 處理)
    ↓
┌─────────────────┬─────────────────┐
│ 本地完整版      │ Supabase 精簡版 │
│ data/memories/  │ memories 表     │
└─────────────────┴─────────────────┘
```

### AI 查詢
```
使用者問題
    ↓
chat.py
    ↓
rag.py (向量搜尋)
    ↓
讀取相關記憶
    ↓
回答
```

---

## 🔧 開發工具

### 讀取記憶
```python
from tools.ai_memory_reader import read_daily_memory

# 讀取今天的記憶
memory = await read_daily_memory("2026-02-17")
```

### 查詢資料庫
```python
from tools.ai_memory_reader import read_monthly_review

# 讀取月度總結
review = await read_monthly_review(2026, 2)
```

### URL 討論（新！）
```python
# 測試 URL 抓取
import requests
res = requests.post("http://localhost:8000/api/v1/url/fetch", json={"url": "https://..."})
print(res.json())
```

### 生成月報（新！）
```bash
python tools/generate_monthly_review.py 2026 1
```

### 追蹤任務
```python
# 手動追加任務完成
python tools/task_tracker.py "完成 XXX 功能"
```

---

## ✅ 當前進度

### 已完成
- ✅ Phase 1: RAG Infrastructure
- ✅ Phase 2: Cognitive Awakening
- ✅ 本地優先架構
- ✅ Append Mode

### 待完成
- ⏳ Phase 3: Agentic Automation
  - Daily Reflection Agent
  - APScheduler Integration

---

## 🚨 重要提醒

### 不要混淆
- **系統 AI** = `app/` 目錄（服務使用者）
- **開發 AI** = `tools/` 目錄（開發系統）

### 必讀檔案
1. `.cursorrules` - 開發規則
2. `evolution_log.json` - 演化歷史
3. `SYSTEM_CONTEXT.md` - 系統架構

---

## 🧪 測試工作流程

### tests/ 目錄規則
```
backend-cortex/tests/
├── test_feature_name.py    # 測試檔案
└── ...
```

### ⚠️ 重要原則
1. **測試是臨時的** - 測試完成後刪除
2. **先看測試** - 開始開發前先看 `tests/` 目錄
3. **修補主程式** - 測試通過後，修補 `app/` 主程式
4. **刪除測試** - 主程式修好後，刪除測試檔案

### 工作流程
```bash
# 1. 先看測試
ls tests/

# 2. 執行測試
python tests/test_feature_name.py

# 3. 根據測試結果修補主程式
# 編輯 app/...

# 4. 測試通過後刪除
rm tests/test_feature_name.py
```

---

## 🔧 開發工具
```bash
python tools/cortex_sync.py
```

---

## ☁️ 雲端同步工作流程（重要！）

### 開始開發前
```bash
# 1. 先檢查雲端最新版本
G:\我的雲端硬碟\Cortex\

# 2. 確認這些檔案是否比本地新
- AI_MEMORY.md
- DATABASE_SCHEMA.md
- task.md
- evolution_log.json
- .cursorrules

# 3. 如果雲端較新，先合併到本地
# 手動比對差異，合併重要更新
```

### 開發完成後
```bash
# 1. 同步到雲端
python tools/cortex_sync.py

# 2. 確認同步成功
# 檢查 G:\我的雲端硬碟\Cortex\tools\ 目錄

# 3. 更新 evolution_log.json
# 記錄這次開發的變更
```

### 雲端檔案結構
```
G:\我的雲端硬碟\Cortex\
├── tools/              # 開發工具和文檔
│   ├── START_HERE.md
│   ├── AI_MEMORY.md
│   ├── DATABASE_SCHEMA.md
│   └── task.md
├── code_backup/        # 核心程式碼備份
├── migrations/         # 資料庫遷移
├── .cursorrules
├── evolution_log.json
└── SYSTEM_CONTEXT.md
```

### ⚠️ 重要提醒
1. **永遠先檢查雲端版本** - 避免覆蓋其他 AI 的工作
2. **開發完立刻同步** - 確保雲端是最新狀態
3. **記錄變更** - 更新 `evolution_log.json`

---

## 📝 下一步

1. 讀完這 3 個檔案
2. 查看 `task.md` 當前任務
3. 開始開發

**就這麼簡單！**
