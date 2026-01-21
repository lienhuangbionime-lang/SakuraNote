import os
import json
import glob
import requests

# 這是你的 Zapier Webhook URL (需在 Zapier 建立一個 "Catch Hook")
ZAPIER_TASK_WEBHOOK = os.getenv("ZAPIER_TASK_WEBHOOK") 

def sync_tasks_to_cloud():
    # 1. 讀取 Inbox 裡剛生成的 JSON (還沒被壓縮的)
    inbox_files = glob.glob("data/inbox/*.json")
    
    tasks_to_sync = []
    
    for filepath in inbox_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 2. 提取待辦事項 (根據你的 Dual-Track 結構)
        # 假設 Gemini 分析結果在 analysis.project_data.open_nodes 或 summary
        analysis = data.get('analysis', {})
        p_data = analysis.get('project_data', {})
        
        # 策略 A: 抓取 Open Nodes
        open_nodes = p_data.get('open_nodes', '')
        if open_nodes and open_nodes != 'None':
            # 簡單清洗：如果是條列式，拆開
            nodes = [n.strip('- ').strip() for n in open_nodes.split('\n') if n.strip()]
            for node in nodes:
                tasks_to_sync.append({
                    "title": f"[LifeOS] {node}",
                    "notes": f"Source: {data.get('date')} Log\nProject: {p_data.get('candidates', ['Unknown'])[0]}",
                    "due": "tomorrow" # 預設明天
                })

        # 策略 B: 抓取 Life MIT (Most Important Thing)
        # 如果你有在 analysis 裡特別提取 MIT
        
    # 3. 發送給 Zapier
    if tasks_to_sync and ZAPIER_TASK_WEBHOOK:
        print(f"🚀 Syncing {len(tasks_to_sync)} tasks to Google Tasks...")
        try:
            requests.post(ZAPIER_TASK_WEBHOOK, json={"tasks": tasks_to_sync})
            print("✅ Sync request sent.")
        except Exception as e:
            print(f"❌ Sync failed: {e}")
    else:
        print("No tasks found or Webhook not set.")

if __name__ == "__main__":
    sync_tasks_to_cloud()
