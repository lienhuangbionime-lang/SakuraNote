# LifeOS Backend 啟動指南

## 🚀 啟動後端

### 方法 1: 直接啟動
```bash
cd C:\Users\benga\Desktop\lifeosjxs-main\backend-cortex
python main.py
```

### 方法 2: 使用 uvicorn
```bash
cd C:\Users\benga\Desktop\lifeosjxs-main\backend-cortex
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ 確認運行

啟動後應該看到：
```
[SCHEDULER] Subconscious Scheduler Started
[SCHEDULER] Daily Reflection scheduled at 23:00
[WORKER] Subconscious Embedding Process Initiated
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🧪 測試連線

### 瀏覽器測試
```
http://localhost:8000
```

應該回傳：
```json
{
  "system": "LifeOS Cortex",
  "status": "Online",
  "version": "7.1-BrainLink",
  "philosophy": "Autopoiesis"
}
```

### Chat 測試
```
POST http://localhost:8000/api/v1/chat/message
{
  "message": "你好",
  "history": []
}
```

## ⚠️ 常見問題

### Port 已被佔用
```bash
# 查看 8000 port
netstat -ano | findstr :8000

# 終止進程
taskkill /PID <PID> /F
```

### 缺少依賴
```bash
pip install -r requirements.txt
```

### 環境變數未設定
檢查 `.env` 檔案：
```
GEMINI_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```
