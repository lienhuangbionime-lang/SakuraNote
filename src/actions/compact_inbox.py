# 檔案位置: src/actions/compact_inbox.py

import pandas as pd
import glob
import os
import json
import frontmatter
import shutil

# 定義路徑
INBOX_PATH = "data/inbox/"
ARCHIVE_PARQUET_PATH = "data/archive/journal.parquet"
ARCHIVE_JSON_PATH = "data/archive/lifeos_db.json" # [NEW] 前端專用資料庫

# 新增一個分析函數，在 compaction_process 寫入 JSON 前呼叫
def generate_system_state(df):
    """
    計算專案索引、想法交集與系統降速狀態
    """
    # 1. 自動專案索引 (Gardener Logic)
    # 邏輯：統計過去 30 天 Tags 出現頻率 > 3 次
    recent_df = df.head(30) # 假設已倒序
    tag_counts = {}
    # ... (統計 tag 頻率的代碼) ...
    active_projects = [tag for tag, count in tag_counts.items() if count >= 3]

    # 2. 想法萃取 (Idea Generator)
    # 邏輯：找出同時有 Signal + BlindSpot + OpenNodes 的日記
    ideas = []
    for _, row in recent_df.iterrows():
        p_data = row.get('project_data', {})
        if p_data.get('signals') and p_data.get('blind_spots') and p_data.get('open_nodes'):
            ideas.append({
                "date": row['date'],
                "core_concept": f"{p_data['signals'][:20]}... + {p_data['open_nodes'][:20]}..."
            })

    # 3. 生活降速機制 (The Governor)
    # 邏輯：檢查最後 2 筆 Life Log
    last_2_days = df.head(2)
    throttle_mode = "BUILD" # 預設模式
    reason = "All Systems Nominal"
    
    for _, row in last_2_days.iterrows():
        life = row.get('life_data', {})
        if life.get('baseline_safety') == 'Intervene' or life.get('energy_stability') == 'Low':
            throttle_mode = "MAINTENANCE"
            reason = f"Safety Protocol Triggered on {row['date']}"
            break
            
    return {
        "active_projects": active_projects,
        "idea_seeds": ideas,
        "system_status": {
            "mode": throttle_mode, // "BUILD" or "MAINTENANCE"
            "reason": reason
        }
    }

# 在 compaction_process 裡：
# ...
# df_export.to_json(ARCHIVE_JSON_PATH...)

# [NEW] 產出系統狀態檔
system_state = generate_system_state(df_combined)
with open("data/archive/system_state.json", "w", encoding="utf-8") as f:
    json.dump(system_state, f, ensure_ascii=False)
print("System State Updated.")

def compaction_process():
    # 1. 檢查是否有新檔案
    md_files = glob.glob(os.path.join(INBOX_PATH, "*.md"))
    if not md_files:
        print("No files to compact.")
        return

    print(f"Starting compaction for {len(md_files)} entries...")

    # 2. 讀取現有 Parquet (作為基底)
    if os.path.exists(ARCHIVE_PARQUET_PATH):
        try:
            df_base = pd.read_parquet(ARCHIVE_PARQUET_PATH)
        except Exception as e:
            print(f"Warning: Could not read parquet, starting fresh. {e}")
            df_base = pd.DataFrame()
    else:
        df_base = pd.DataFrame()

    # 3. 解析 Inbox 資料
    new_data = []
    files_to_delete = []

    for md_file in md_files:
        try:
            # 讀取 MD
            post = frontmatter.load(md_file)
            entry = post.metadata
            
            # 確保有 date 欄位，若無則嘗試從檔名解析或使用今天
            if 'date' not in entry: 
                # 檔名格式通常為 YYYYMMDD_...
                filename = os.path.basename(md_file)
                if filename[:8].isdigit():
                    entry['date'] = f"{filename[:4]}-{filename[4:6]}-{filename[6:8]}"
                else:
                    entry['date'] = str(post.get('date'))[:10] if post.get('date') else "1970-01-01"
            
            # 將內容放入 content 欄位 (前端 LifeOS 習慣讀取 note 或 content)
            entry['content'] = post.content
            entry['note'] = post.content # 雙重保險
            
            # 讀取 JSON Sidecar
            json_file = md_file.replace(".md", ".json")
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    sidecar = json.load(f)
                    # 這裡我們只存必要的分析數據到 Parquet/JSON
                    if 'analysis' in sidecar:
                        entry['ai_analysis'] = sidecar['analysis'] 
                        # 嘗試將 AI 分析的 mood/focus 覆蓋回去，如果原本沒有的話
                        if 'mood' not in entry and 'mood' in sidecar['analysis']:
                            entry['mood'] = sidecar['analysis']['mood']
                    
                    # Embedding 存入 Parquet 供 Python RAG 使用，但不存入前端 JSON
                    entry['embedding'] = sidecar.get('embedding') 
                    
                files_to_delete.append(json_file)
            
            files_to_delete.append(md_file)
            new_data.append(entry)
            
        except Exception as e:
            print(f"Error compacting {md_file}: {e}")

    # 4. 合併與寫入
    if new_data:
        df_new = pd.DataFrame(new_data)
        
        # 確保格式一致
        if 'date' in df_new.columns:
            df_new['date'] = pd.to_datetime(df_new['date'])
        if not df_base.empty and 'date' in df_base.columns:
            df_base['date'] = pd.to_datetime(df_base['date'])

        df_combined = pd.concat([df_base, df_new], ignore_index=True)
        
        # 去重 (以 uuid 為主，或以 date 為主)
        if 'uuid' in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset=['uuid'], keep='last')
        else:
            df_combined = df_combined.drop_duplicates(subset=['date'], keep='last')

        # 排序
        df_combined = df_combined.sort_values(by='date')

        # [OUTPUT 1] 寫入 Parquet (給機器/RAG用)
        # 建立目錄確保存在
        os.makedirs(os.path.dirname(ARCHIVE_PARQUET_PATH), exist_ok=True)
        df_combined.to_parquet(ARCHIVE_PARQUET_PATH, compression='snappy')
        print(f"Compacted to {ARCHIVE_PARQUET_PATH}")

        # [OUTPUT 2] 寫入 JSON (給 HTML 前端用)
        # 移除 embedding 欄位以縮減 JSON 大小，並將日期轉字串
        df_export = df_combined.copy()
        if 'embedding' in df_export.columns:
            df_export = df_export.drop(columns=['embedding'])
        if 'date' in df_export.columns:
            df_export['date'] = df_export['date'].dt.strftime('%Y-%m-%d')
        
        # 處理 metrics 結構 (如果你的 HTML 需要 metrics 物件)
        # 這裡假設 DataFrame 是攤平的 (mood, focus...)，匯出時保持攤平，前端 sanitizeLogEntry 會處理
            
        df_export.to_json(ARCHIVE_JSON_PATH, orient='records', force_ascii=False, date_format='iso')
        print(f"Exported JSON to {ARCHIVE_JSON_PATH}")

        # 5. 清理 Inbox
        for f in files_to_delete:
            if os.path.exists(f):
                os.remove(f)
        print("Inbox cleaned.")

if __name__ == "__main__":
    compaction_process()
