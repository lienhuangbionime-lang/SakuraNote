import pandas as pd
import glob
import os
import json
import sys

# [Path Fix]
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.analytics import generate_system_state

# 定義路徑
INBOX_PATH = "data/inbox/"
ARCHIVE_PARQUET_PATH = "data/archive/journal.parquet"
ARCHIVE_JSON_PATH = "data/archive/lifeos_db.json"
SYSTEM_STATE_PATH = "data/archive/system_state.json"

def compaction_process():
    # ... (此處可考慮進一步重構，目前為保持最小變動，僅替換 generate_system_state 邏輯)
    # 這裡的邏輯與 compact_inbox.py 幾乎一致，建議長期只需保留一個。
    # 為了回應 Priority 2，我們確保此檔案也使用新的 analytics 模組。
    
    # 1. 檢查是否有新檔案 (同 compact_inbox)
    md_files = glob.glob(os.path.join(INBOX_PATH, "*.md"))
    if not md_files and not os.path.exists(ARCHIVE_PARQUET_PATH):
        return
            
    # 2. 讀取現有 Parquet
    if os.path.exists(ARCHIVE_PARQUET_PATH):
        try:
            df_base = pd.read_parquet(ARCHIVE_PARQUET_PATH)
        except Exception as e:
            print(f"Warning: Could not read parquet. {e}")
            df_base = pd.DataFrame()
    else:
        df_base = pd.DataFrame()

    # (省略中間解析步驟，因為 generate_report 主要用途若是生成報告，應該依賴已歸檔的資料)
    # 假設這裡我們主要想測試生成 System State
    
    if not df_base.empty:
         # 確保是日期倒序
        df_sorted = df_base.sort_values(by='date', ascending=False)
        
        try:
            print("Analyzing System State (Report Mode)...")
            system_state = generate_system_state(df_sorted)
            # 這裡可以做不同的輸出，例如打印報告
            print(json.dumps(system_state, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ System State Generation Failed: {e}")

if __name__ == "__main__":
    compaction_process()
