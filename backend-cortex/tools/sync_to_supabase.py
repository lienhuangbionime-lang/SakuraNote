"""
Sync Local Memories to Supabase
Purpose: Upload all local memory files to Supabase for BRAIN visualization
"""

import os
import sys
import json
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    import google.generativeai as genai
    from app.core.database import supabase
    
    ENABLE_EMBEDDING = True
    ENABLE_SUPABASE = supabase is not None
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    sys.exit(1)


def sync_single_memory(filepath: str, index: int, total: int) -> bool:
    """
    同步單個記憶檔案到 Supabase
    """
    try:
        filename = os.path.basename(filepath)
        date = filename.replace('.json', '')
        
        print(f"[{index}/{total}] Syncing {date}...")
        
        # 1. 讀取本地檔案
        with open(filepath, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        combined_content = memory.get('combined_content', '')
        if not combined_content:
            print(f"  [SKIP] Empty content")
            return False
        
        # 2. 生成 embedding
        embedding = None
        if ENABLE_EMBEDDING:
            try:
                content_for_embedding = combined_content[:8000]
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=content_for_embedding,
                    task_type="retrieval_document"
                )
                embedding = result['embedding']
                print(f"  [OK] Generated embedding ({len(embedding)} dims)")
            except Exception as e:
                print(f"  [WARN] Embedding failed: {e}")
        
        # 3. 準備 Supabase payload
        content_hash = hashlib.sha256(combined_content.encode()).hexdigest()
        
        # 從第一個 entry 取得 metadata
        first_entry = memory.get('entries', [{}])[0]
        metadata = first_entry.get('metadata', {})
        
        db_payload = {
            "date": date,
            "local_path": filename,
            "content_hash": content_hash,
            "ai_insights": combined_content,  # Full content for BRAIN tag parsing
            "mood": metadata.get('mood', 5),
            "focus": metadata.get('focus', 5),
            "energy": metadata.get('energy', 5),
            "tags": [],
            "is_ai": metadata.get('is_ai', False),
            "ai_model": metadata.get('ai_model', 'unknown'),
            "created_at": memory.get('created_at'),
            "updated_at": memory.get('updated_at')
        }
        
        if embedding:
            db_payload["embedding"] = embedding
        
        # 4. Upsert 到 Supabase
        if not supabase:
            print(f"  [ERROR] Supabase not available")
            return False
        
        supabase.table("memories").upsert(db_payload, on_conflict="date").execute()
        print(f"  [OK] Synced to Supabase")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        return False


def sync_all_memories():
    """
    同步所有本地記憶到 Supabase
    """
    print("=" * 60)
    print("Sync Local Memories to Supabase")
    print("=" * 60)
    
    # 找到所有記憶檔案
    memory_dir = "data/memories"
    if not os.path.exists(memory_dir):
        print(f"[ERROR] Directory not found: {memory_dir}")
        return
    
    files = sorted([
        os.path.join(memory_dir, f) 
        for f in os.listdir(memory_dir) 
        if f.endswith('.json')
    ])
    
    print(f"\n[INFO] Found {len(files)} memory files")
    print(f"[INFO] Embedding: {'Enabled' if ENABLE_EMBEDDING else 'Disabled'}")
    print()
    
    # 逐一同步
    success_count = 0
    for i, filepath in enumerate(files, 1):
        if sync_single_memory(filepath, i, len(files)):
            success_count += 1
        
        # 每 10 筆暫停一下（避免 API rate limit）
        if i % 10 == 0 and i < len(files):
            print(f"\n[INFO] Processed {i}/{len(files)}, pausing 2 seconds...\n")
            import time
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"Sync Complete: {success_count}/{len(files)} successful")
    print("=" * 60)
    print(f"\n[INFO] Supabase table: memories")
    print(f"[INFO] You can now use BRAIN visualization")


if __name__ == "__main__":
    sync_all_memories()
