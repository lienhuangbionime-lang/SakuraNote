# src/actions/sync_tasks.py
import os
import json
import glob
import requests
import time

ZAPIER_TASK_WEBHOOK = os.getenv("ZAPIER_TASK_WEBHOOK") 

def sync_tasks_to_cloud():
    inbox_files = glob.glob("data/inbox/*.json")
    tasks_to_sync = []
    
    for filepath in inbox_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis = data.get('analysis', {})
            date_str = data.get('date', 'Unknown Date')
            
            # 1. 讀取 AI 提取的任務
            ai_actions = analysis.get('action_items', [])
            
            if ai_actions:
                print(f"✅ Found {len(ai_actions)} tasks in {filepath}")
                for item in ai_actions:
                    # 相容性處理
                    if isinstance(item, str):
                        task_title = item
                        priority = "Med"
                        context = ""
                    else:
                        task_title = item.get('task', 'Untitled Task')
                        priority = item.get('priority', 'Med')
                        context = item.get('context', '')

                    tasks_to_sync.append({
                        "title": f"[LifeOS] {task_title}",
                        "notes": f"📅 {date_str} | 🔥 {priority}\nContext: {context}",
                        "due": "tomorrow"
                    })

        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        
    # 2. [優化] 迴圈發送 (確保 Zapier 每一條都收到)
    if tasks_to_sync and ZAPIER_TASK_WEBHOOK:
        print(f"🚀 Syncing {len(tasks_to_sync)} tasks to Zapier...")
        
        for i, task in enumerate(tasks_to_sync):
            try:
                # 直接發送單一任務物件，Zapier 比較好讀取
                requests.post(ZAPIER_TASK_WEBHOOK, json=task)
                print(f"✅ Sent ({i+1}/{len(tasks_to_sync)}): {task['title']}")
                time.sleep(1) # 休息 1 秒，避免 Zapier 覺得我們是機器人攻擊
            except Exception as e:
                print(f"❌ Send failed: {e}")
                
    else:
        print("No tasks found or Webhook not set.")

if __name__ == "__main__":
    sync_tasks_to_cloud()
