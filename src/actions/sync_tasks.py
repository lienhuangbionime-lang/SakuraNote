# src/actions/sync_tasks.py
import os
import json
import glob
import requests

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
            
            # --- [修改處]：優先讀取 AI 明確提取的 action_items ---
            ai_actions = analysis.get('action_items', [])
            
            if ai_actions:
                print(f"✅ Found {len(ai_actions)} AI-extracted tasks in {filepath}")
                for item in ai_actions:
                    # 相容性處理：如果 AI 回傳字串而非物件
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
            
            # (可選) 保留 open_nodes 作為備案，但建議移除以避免重複
            # 原本的 Open Nodes 邏輯已刪除，確保「只聽 AI 的」

        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        
    if tasks_to_sync and ZAPIER_TASK_WEBHOOK:
        print(f"🚀 Syncing {len(tasks_to_sync)} tasks to Zapier...")
        try:
            # 這裡要注意 Zapier Webhook 是否接受 "tasks" 陣列
            # 如果你的 Zapier 設定是 "Catch Hook"，它通常可以解析 JSON 陣列
            requests.post(ZAPIER_TASK_WEBHOOK, json={"tasks": tasks_to_sync})
            print("✅ Sync request sent.")
        except Exception as e:
            print(f"❌ Sync failed: {e}")
    else:
        print("No tasks found or Webhook not set.")

if __name__ == "__main__":
    sync_tasks_to_cloud()
