import os
import json
import re
import glob
import datetime

# 定義路徑
INBOX_DIR = "data/inbox"
PROJECTS_DIR = "data/projects"
LIFE_DIR = "data/life"
STATUS_DIR = "data/status" # [NEW] 狀態目錄

def parse_dual_track(raw_text):
    # ... (原本的 A/B 拆解邏輯保持不變) ...
    # 1. 切割 A. Project Log
    project_match = re.search(r'## A\. Project Log.*?([\s\S]*?)(?=## B\. Life Log|$)', raw_text, re.IGNORECASE)
    project_content = project_match.group(1).strip() if project_match else ""

    # 2. 切割 B. Life Log
    life_match = re.search(r'## B\. Life Log.*?([\s\S]*?)(?=## Graph Seeds|$)', raw_text, re.IGNORECASE)
    life_content = life_match.group(1).strip() if life_match else ""

    # 3. 提取 Project Tags
    tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', project_content)
    valid_project_tags = [t for t in tags if t not in ['LifeOS', 'DualMemory'] or t == 'LifeOS'] 
    primary_project = valid_project_tags[0] if valid_project_tags else "Uncategorized"

    # [NEW] 4. 提取 Tomorrow's MIT (下一步行動)
    # 抓取 "Tomorrow’s MIT" 或 "Next Step" 下方的列表項目
    mit_match = re.search(r'(?:Tomorrow’s MIT|Next Steps).*?\n([\s\S]*?)(?=\n###|\n---|$)', project_content, re.IGNORECASE)
    next_actions = []
    if mit_match:
        # 抓取所有以 - 或 * 開頭的行
        raw_actions = mit_match.group(1).strip()
        next_actions = re.findall(r'^\s*[-*]\s*(.*)', raw_actions, re.MULTILINE)

    return {
        "project": {
            "name": primary_project,
            "content": project_content,
            "tags": tags,
            "next_actions": next_actions # [NEW]
        },
        "life": {
            "content": life_content
        }
    }

def process_inbox_files():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(LIFE_DIR, exist_ok=True)
    os.makedirs(STATUS_DIR, exist_ok=True) # [NEW]

    files = glob.glob(os.path.join(INBOX_DIR, "*.json"))
    
    current_actions = {} # 用來收集本次處理的所有下一步

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        raw_text = data.get('raw_text', '') or data.get('note', '')
        date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        if not raw_text:
            continue
            
        parsed = parse_dual_track(raw_text)
        
        # --- 路由 1: 專案日誌 ---
        project_name = parsed['project']['name']
        project_file = os.path.join(PROJECTS_DIR, f"{project_name}.md")
        
        with open(project_file, 'a', encoding='utf-8') as pf:
            entry_block = f"\n\n### {date} Log\n{parsed['project']['content']}\n\n---"
            pf.write(entry_block)

        # [NEW] 處理下一步行動
        if parsed['project']['next_actions']:
            current_actions[project_name] = {
                "date": date,
                "actions": parsed['project']['next_actions']
            }
            
        # --- 路由 2: 生活訊號 ---
        life_file = os.path.join(LIFE_DIR, f"life_log_{date[:7]}.md")
        with open(life_file, 'a', encoding='utf-8') as lf:
            entry_block = f"\n\n### {date}\n{parsed['life']['content']}\n\n---"
            lf.write(entry_block)

    # [NEW] 輸出 "Active Context" 檔案
    # 這檔案只包含「最新」的下一步，Action 跑完後可以讀取這個檔案來發送通知
    if current_actions:
        with open(os.path.join(STATUS_DIR, "latest_actions.json"), "w", encoding="utf-8") as f:
            json.dump(current_actions, f, ensure_ascii=False, indent=2)
            print(f"✅ Extracted Next Actions: {list(current_actions.keys())}")

if __name__ == "__main__":
    process_inbox_files()
