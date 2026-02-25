import os
import sys
import json
import logging
import re
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add app root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # Up from tools/ -> backend-cortex/ -> root
backend_root = os.path.dirname(current_dir) # backend-cortex

sys.path.append(backend_root)

# Load environment variables BEFORE importing app modules that use them
load_dotenv(os.path.join(backend_root, '.env'))

try:
    from app.core.database import supabase
except ImportError:
    # Fallback if path issue
    logger.warning("Could not import app.core.database. Supabase sync will be disabled.")
    supabase = None

def import_file(filepath: str):
    """
    Import a single memory file (JSON or MD) into LifeOS system.
    Steps:
    1. Parse date from filename.
    2. Convert content to standardized JSON memory format.
    3. Save to local data/memories/.
    4. Upsert to Supabase.
    """
    path = Path(filepath)
    filename = path.name
    
    # 1. Parse Date (YYYY-MM-DD)
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if not date_match:
        logger.error(f"Skipping {filename}: No date found in filename (Format: YYYY-MM-DD)")
        return False
    
    date_str = date_match.group(1)
    
    # 2. Read Content
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read {filename}: {e}")
        return False

    # 3. Process Data
    memory_data = {}
    
    if filename.endswith(".json"):
        try:
            data = json.loads(content)
            # Normalize structure
            # If exported from old system, might differ.
            # Standard LifeOS: { date, content, combined_content, markdown_body, tags, meta, is_ai }
            
            # Map fields
            body = data.get("markdown_body") or data.get("combined_content") or data.get("content") or ""
            tags = data.get("tags") or data.get("meta", {}).get("tags") or []
            meta = data.get("meta") or data.get("metadata") or {}
            is_ai = data.get("is_ai", False)
            
            memory_data = {
                "date": date_str,
                "markdown_body": body,
                "content": body, # Duplicate for compatibility
                "tags": tags,
                "meta": meta,
                "is_ai": is_ai
            }
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {filename}")
            return False

    elif filename.endswith(".md") or filename.endswith(".txt"):
        memory_data = {
            "date": date_str,
            "markdown_body": content,
            "content": content,
            "tags": [],
            "meta": {"source": "manual_import"},
            "is_ai": False
        }
    
    else:
        logger.warning(f"Skipping {filename}: Unsupported extension")
        return False

    # 4. Save Local
    local_dir = Path(backend_root) / "data" / "memories"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / f"{date_str}.json"
    
    try:
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved local: {local_path}")
    except Exception as e:
        logger.error(f"Failed to write local file {local_path}: {e}")
        return False

    # 5. Sync to Supabase
    if supabase:
        try:
            db_entry = {
                "date": date_str,
                "content": memory_data["markdown_body"],
                "tags": memory_data["tags"],
                "metadata": memory_data["meta"],
                "is_ai": memory_data["is_ai"]
            }
            
            res = supabase.table("memories").upsert(db_entry, on_conflict="date").execute()
            logger.info(f"Synced to Supabase: {date_str}")
        except Exception as e:
            logger.error(f"Failed to sync to Supabase: {e}")
            # Don't fail entire import if DB fails, but log it.
    else:
        logger.warning("Supabase client not initialized. Skipping cloud sync.")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/import_backup.py <file_or_directory>")
        sys.exit(1)
        
    target = Path(sys.argv[1])
    
    if not target.exists():
        logger.error(f"Path not found: {target}")
        sys.exit(1)
        
    if target.is_file():
        import_file(str(target))
    elif target.is_dir():
        logger.info(f"Scanning directory: {target}")
        files = list(target.glob("*.json")) + list(target.glob("*.md"))
        logger.info(f"Found {len(files)} potential backup files.")
        
        success_count = 0
        for f in files:
            if import_file(str(f)):
                success_count += 1
                
        logger.info(f"Import complete. Imported {success_count}/{len(files)} files.")

if __name__ == "__main__":
    main()
