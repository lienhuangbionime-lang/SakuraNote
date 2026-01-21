import os
import json
import re
import glob
import datetime

# 定義路徑
INBOX_DIR = "data/inbox"
PROJECTS_DIR = "data/projects"
LIFE_DIR = "data/life"

def parse_dual_track(raw_text):
    """
    手術刀：將日記文本拆解為 Project 與 Life 兩部分
    """
    # 1. 切割 A. Project Log
    project_match = re.search(r'## A\. Project Log.*?([\s\S]*?)(?=## B\. Life Log|$)', raw_text, re.IGNORECASE)
    project_content = project_match.group(1).strip() if project_match else ""

    # 2. 切割 B. Life Log
    life_match = re.search(r'## B\. Life Log.*?([\s\S]*?)(?=## Graph Seeds|$)', raw_text, re.IGNORECASE)
    life_content = life_match.group(1).strip() if life_match else ""

    # 3. 提取 Project Tags (作為資料夾分類依據)
    # 找尋 #Tag 格式，排除 #Project
    tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', project_content)
    # 過濾掉一些結構性 Tag
    valid_project_tags = [t for t in tags if t not in ['LifeOS', 'DualMemory'] or t == 'LifeOS'] 
    # 這裡你可以自定義邏輯：取第一個主要 Tag 當作 Project Name
    primary_project = valid_project_tags[0] if valid_project_tags else "Uncategorized"

    # 4. 提取 Project Status (Highlights, Open Nodes)
    # 這裡可以用更細的 Regex 抓取 highlights，這裡先抓整塊
    
    return {
        "project": {
            "name": primary_project,
            "content": project_content,
            "tags": tags
        },
        "life": {
            "content": life_content
        }
    }

def process_inbox_files():
    # 確保輸出目錄存在
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(LIFE_DIR, exist_ok=True)

    # 讀取 Inbox 所有 json (假設我們只處理還沒被 Archive 的)
    # 實務上，你可以讓 Action 傳入特定的 filename，這裡示範批次處理
    files = glob.glob(os.path.join(INBOX_DIR, "*.json"))
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        raw_text = data.get('raw_text', '') or data.get('note', '') # 兼容欄位
        date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        if not raw_text:
            continue
            
        # 執行切割
        parsed = parse_dual_track(raw_text)
        
        # --- 路由 1: 專案日誌 (Project Router) ---
        project_name = parsed['project']['name']
        project_file = os.path.join(PROJECTS_DIR, f"{project_name}.md")
        
        # 將專案進度「追加」到該專案的專屬檔案中 (Append-Only Log)
        with open(project_file, 'a', encoding='utf-8') as pf:
            entry_block = f"\n\n### {date} Log\n{parsed['project']['content']}\n\n---"
            pf.write(entry_block)
            
        print(f"✅ Routed Project Log to: {project_file}")

        # --- 路由 2: 生活訊號 (Life Signal Router) ---
        # Life Log 可以統一存，或者按月份存
        life_file = os.path.join(LIFE_DIR, f"life_log_{date[:7]}.md") # e.g., life_log_2026-01.md
        
        with open(life_file, 'a', encoding='utf-8') as lf:
            entry_block = f"\n\n### {date}\n{parsed['life']['content']}\n\n---"
            lf.write(entry_block)
            
        print(f"✅ Routed Life Log to: {life_file}")

if __name__ == "__main__":
    process_inbox_files()
