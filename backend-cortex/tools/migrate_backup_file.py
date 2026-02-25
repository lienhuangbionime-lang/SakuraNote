"""
LifeOS Backup File Migration Tool
Purpose: Migrate life_os_backup_*.json to new format
Usage: python tools/migrate_backup_file.py <backup_file_path>
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path setup
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    import google.generativeai as genai
    from app.core.database import get_supabase
    
    ENABLE_SUPABASE = True
    ENABLE_EMBEDDING = True
except ImportError as e:
    print(f"[WARN] Some features disabled: {e}")
    ENABLE_SUPABASE = False
    ENABLE_EMBEDDING = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def migrate_single_log(log: Dict, index: int, total: int) -> bool:
    """
    遷移單筆日記
    """
    try:
        date = log.get("date")
        if not date:
            print(f"[SKIP] Log {index}/{total}: No date field")
            return False
        
        print(f"[{index}/{total}] Processing {date}...")
        
        # 1. 轉換成新格式
        new_format = {
            "id": f"migrated_{date}",
            "date": date,
            "entries": [{
                "time": datetime.fromtimestamp(log.get("timestamp", 0) / 1000).isoformat() if log.get("timestamp") else datetime.now().isoformat(),
                "content": log.get("note", ""),
                "ai_processed": log.get("note", ""),  # 舊版已經是 AI 處理後的
                "metadata": {
                    "mood": log.get("metrics", {}).get("mood", 5),
                    "focus": log.get("metrics", {}).get("focus", 5),
                    "energy": log.get("metrics", {}).get("energy", 5),
                    "tags": [],
                    "is_ai": True,
                    "ai_model": "legacy"
                }
            }],
            "combined_content": log.get("note", ""),
            "created_at": datetime.fromtimestamp(log.get("timestamp", 0) / 1000).isoformat() if log.get("timestamp") else datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 2. 寫入本地
        local_dir = "data/memories"
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, f"{date}.json")
        
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(new_format, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] Saved to local: {date}.json")
        
        # 3. 生成 embedding (optional)
        embedding = None
        if ENABLE_EMBEDDING:
            try:
                content_for_embedding = new_format["combined_content"][:8000]
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=content_for_embedding,
                    task_type="retrieval_document"
                )
                embedding = result['embedding']
                print(f"  [OK] Generated embedding")
            except Exception as e:
                print(f"  [WARN] Embedding failed: {e}")
        
        # 4. 寫入 Supabase (optional)
        if ENABLE_SUPABASE:
            try:
                supabase = get_supabase()
                if supabase:
                    content_hash = hashlib.sha256(new_format["combined_content"].encode()).hexdigest()
                    
                    db_payload = {
                        "date": date,
                        "local_path": f"{date}.json",
                        "content_hash": content_hash,
                        "ai_insights": new_format["combined_content"][:500],
                        "mood": log.get("metrics", {}).get("mood", 5),
                        "focus": log.get("metrics", {}).get("focus", 5),
                        "energy": log.get("metrics", {}).get("energy", 5),
                        "tags": [],
                        "created_at": new_format["created_at"],
                        "updated_at": new_format["updated_at"]
                    }
                    
                    if embedding:
                        db_payload["embedding"] = embedding
                    
                    supabase.table("memories").upsert(db_payload, on_conflict="date").execute()
                    print(f"  [OK] Synced to Supabase")
            except Exception as e:
                print(f"  [WARN] Supabase sync failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        return False


def migrate_backup_file(backup_file: str):
    """
    遷移整個備份檔案
    """
    print("=" * 60)
    print("LifeOS Backup Migration Tool")
    print("=" * 60)
    
    if not os.path.exists(backup_file):
        print(f"[ERROR] File not found: {backup_file}")
        return
    
    # 讀取備份檔案
    print(f"\n[INFO] Reading backup file...")
    with open(backup_file, "r", encoding="utf-8") as f:
        backup_data = json.load(f)
    
    logs = backup_data.get("logs", [])
    print(f"[INFO] Found {len(logs)} diary entries")
    print(f"[INFO] Backup version: {backup_data.get('version', 'unknown')}")
    
    # 逐一遷移
    success_count = 0
    for i, log in enumerate(logs, 1):
        if migrate_single_log(log, i, len(logs)):
            success_count += 1
        
        # 每 10 筆暫停一下
        if i % 10 == 0:
            print(f"\n[INFO] Processed {i}/{len(logs)}, pausing 1 second...\n")
            import time
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"Migration Complete: {success_count}/{len(logs)} successful")
    print("=" * 60)
    print(f"\n[INFO] Local files: data/memories/")
    if ENABLE_SUPABASE:
        print(f"[INFO] Supabase table: memories")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tools/migrate_backup_file.py <backup_file>")
        print("Example: python tools/migrate_backup_file.py G:\\我的雲端硬碟\\Cortex\\life_os_backup_2026-01-03.json")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    migrate_backup_file(backup_file)
