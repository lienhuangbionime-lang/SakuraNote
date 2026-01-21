import os
import json
import re
import glob
import datetime
import requests # 需要在 process_journal.yml 安裝 requests

# 定義路徑
INBOX_DIR = "data/inbox"
PROJECTS_DIR = "data/projects"
LIFE_DIR = "data/life"

# [NEW] Zapier Webhook URL (從 Secrets 讀取)
ZAPIER_TASK_WEBHOOK = os.getenv("ZAPIER_TASK_WEBHOOK")

def extract_tasks(content):
    """
    從日記內容中抓取待辦事項
    支援格式：
    1. Tomorrow's MIT:
       - 任務 A
    2. [ ] 任務 B
    """
    tasks = []
    
    # 模式 A: 抓取 Tomorrow's MIT 區塊
    mit_match = re.search(r"Tomorrow's MIT.*?(\n(?:[-*].*?|\s*)*)(?=\n#|\n\n|$)", content, re.IGNORECASE | re.DOTALL)
    if mit_match:
        lines = mit_match.group(1).strip().split('\n')
        for line in lines:
            clean_line = re.sub(r"^[-*]\s*", "", line).strip()
            if clean_line:
                tasks.append(clean_line)

    # 模式 B: 抓取未完成的 Checkbox [ ]
    checkboxes = re.findall(r"-\s*\[\s*\]\s*(.*)", content)
    tasks.extend(checkboxes)

    return list(set(tasks)) # 去重

def send_to_zapier(tasks, date):
    if not ZAPIER_TASK_WEBHOOK:
        print("⚠️ No ZAPIER_TASK_WEBHOOK configured. Skipping task sync.")
        return

    for task in tasks:
        try:
            payload = {"title": task, "date": date, "source": "LifeOS"}
            requests.post(ZAPIER_TASK_WEBHOOK, json=payload)
            print(f"🚀 Sent to Zapier: {task}")
        except Exception as e:
            print(f"❌ Failed to send task: {e}")

def parse_dual_track(raw_text):
    # ... (保留你原本的切割邏輯) ...
    # 1. 切割 A. Project Log ...
    # 2. 切割 B. Life Log ...
    # 3. 提取 Tags ...
    
    # 這裡為了簡化，直接回傳你原本的 dict 結構
    # (請將你原本的 parse_dual_track 函數內容完整保留)
    # ...
    return {
        "project": { "name": "LifeOS", "content": "..." }, # 範例
        "life": { "content": "..." }
    }

def process_inbox_files():
    # ... (保留原本的目錄建立與讀取邏輯) ...
    
    # 在迴圈內：
    # for filepath in files:
        # ... (讀取 data, raw_text) ...
        
        # 1. 執行切割與存檔 (原本的邏輯)
        # parsed = parse_dual_track(raw_text)
        # ... (寫入 Project MD) ...
        # ... (寫入 Life MD) ...

        # [NEW] 2. 萃取任務並發送
        all_content = raw_text # 或只針對 Project 區塊
        tasks = extract_tasks(all_content)
        if tasks:
            print(f"Found {len(tasks)} tasks. Syncing...")
            send_to_zapier(tasks, date)

if __name__ == "__main__":
    process_inbox_files()
