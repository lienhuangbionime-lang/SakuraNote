"""
Legacy JSON Diary Migration Tool
Purpose: Migrate old JSON diary files to new local-first format
Usage: python tools/migrate_legacy_diaries.py <source_dir>
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List
from app.services.embedder import generate_embedding
from app.core.database import get_supabase


async def migrate_single_diary(source_file: str) -> bool:
    """
    遷移單個舊日記檔案
    
    Args:
        source_file: 舊 JSON 檔案路徑
    
    Returns:
        True if successful
    """
    try:
        # 1. 讀取舊檔案
        with open(source_file, "r", encoding="utf-8") as f:
            old_data = json.load(f)
        
        # 2. 提取日期（假設檔名是 YYYY-MM-DD.json）
        filename = os.path.basename(source_file)
        date = filename.replace(".json", "")
        
        # 3. 轉換成新格式
        new_format = {
            "id": old_data.get("id", f"migrated_{date}"),
            "date": date,
            "entries": [],
            "combined_content": "",
            "created_at": old_data.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat()
        }
        
        # 4. 處理內容（根據舊格式調整）
        if "content" in old_data:
            # 舊格式: 單一 content 欄位
            new_format["entries"].append({
                "time": old_data.get("created_at", datetime.now().isoformat()),
                "content": old_data["content"],
                "ai_processed": old_data.get("ai_processed"),
                "metadata": old_data.get("metadata", {})
            })
            new_format["combined_content"] = old_data["content"]
        
        elif "entries" in old_data:
            # 已經是新格式
            new_format = old_data
        
        # 5. 寫入本地
        local_dir = "data/memories"
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, f"{date}.json")
        
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(new_format, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Migrated local: {date}")
        
        # 6. 生成 embedding
        embedding = await generate_embedding(new_format["combined_content"])
        
        # 7. 寫入 Supabase
        supabase = get_supabase()
        if supabase:
            import hashlib
            content_hash = hashlib.sha256(new_format["combined_content"].encode()).hexdigest()
            
            db_payload = {
                "date": date,
                "local_path": f"{date}.json",
                "content_hash": content_hash,
                "ai_insights": new_format["combined_content"][:500],  # 精簡版
                "embedding": embedding,
                "mood": new_format["entries"][0]["metadata"].get("mood", 5),
                "focus": new_format["entries"][0]["metadata"].get("focus", 5),
                "energy": new_format["entries"][0]["metadata"].get("energy", 5),
                "tags": new_format["entries"][0]["metadata"].get("tags", []),
                "created_at": new_format["created_at"],
                "updated_at": new_format["updated_at"]
            }
            
            # Upsert
            supabase.table("memories").upsert(db_payload, on_conflict="date").execute()
            print(f"[OK] Synced to Supabase: {date}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to migrate {source_file}: {e}")
        return False


async def migrate_directory(source_dir: str):
    """
    遷移整個目錄的舊日記
    
    Args:
        source_dir: 舊日記目錄路徑
    """
    print("=" * 60)
    print("Legacy Diary Migration Tool")
    print("=" * 60)
    
    if not os.path.exists(source_dir):
        print(f"[ERROR] Directory not found: {source_dir}")
        return
    
    # 找出所有 JSON 檔案
    json_files = [
        os.path.join(source_dir, f) 
        for f in os.listdir(source_dir) 
        if f.endswith(".json")
    ]
    
    print(f"\n[INFO] Found {len(json_files)} JSON files")
    
    # 逐一遷移
    success_count = 0
    for json_file in json_files:
        if await migrate_single_diary(json_file):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Migration Complete: {success_count}/{len(json_files)} successful")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tools/migrate_legacy_diaries.py <source_directory>")
        print("Example: python tools/migrate_legacy_diaries.py C:\\old_diaries")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    asyncio.run(migrate_directory(source_dir))
