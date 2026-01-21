import os
import json
import glob
import re

PROJECTS_DIR = "data/projects"
REPORT_OUTPUT = "data/archive/project_report.json"

def generate_report():
    report = []
    
    # 掃描 data/projects/ 下的所有 .md 檔案
    project_files = glob.glob(os.path.join(PROJECTS_DIR, "*.md"))
    
    for p_file in project_files:
        name = os.path.splitext(os.path.basename(p_file))[0]
        
        with open(p_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 計算活躍度 (Entry Count)
        entries = content.count("### ") # 假設每個 Log 都有 ### Date
        
        # 2. 抓取最後更新時間
        last_date_match = re.findall(r'### (\d{4}-\d{2}-\d{2})', content)
        last_activity = last_date_match[-1] if last_date_match else "Unknown"
        
        # 3. 抓取最新狀態 (Snippet)
        # 取最後 200 字作為摘要
        snippet = content[-200:].replace('\n', ' ').strip()
        
        # 4. 判斷狀態 (Active/Stale)
        # 這裡可以加入時間判斷，例如超過 7 天沒更新就是 Stale
        status = "Active" 
        
        report.append({
            "name": name,
            "status": status,
            "entry_count": entries,
            "last_activity": last_activity,
            "snippet": snippet
        })
        
    # 排序：最近更新的在前面
    report.sort(key=lambda x: x['last_activity'], reverse=True)
    
    # 寫入 JSON
    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Generated Project Report: {len(report)} projects.")

if __name__ == "__main__":
    generate_report()
