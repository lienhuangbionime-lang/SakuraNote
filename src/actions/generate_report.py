import os
import json
import glob
import pandas as pd

PROJECTS_DIR = "data/projects"
REPORT_OUTPUT = "data/archive/project_report.json"

def generate_report():
    report = []
    
    # 讀取分類器產生的所有專案 MD 檔
    project_files = glob.glob(os.path.join(PROJECTS_DIR, "*.md"))
    
    for p_file in project_files:
        project_name = os.path.basename(p_file).replace('.md', '')
        
        with open(p_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 簡單分析：計算 Log 數量，抓取最後更新時間
        entries = content.split('---')
        entry_count = len(entries)
        last_update = "Unknown"
        
        # 嘗試從最後一段內容抓日期
        if entries:
            last_entry = entries[-1]
            # 這裡可以加更複雜的 Regex
            
        report.append({
            "name": project_name,
            "entry_count": entry_count,
            "status": "Active", # 未來可以用 Gemini 判斷狀態
            "last_activity": "Recently",
            "snippet": content[-200:] # 取最後 200 字給前端顯示
        })
        
    # 寫入 JSON 給前端用
    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated Project Report: {len(report)} projects.")

if __name__ == "__main__":
    generate_report()
