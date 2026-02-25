"""
Task Completion Hook - Automatic Progress Tracking
Purpose: When tasks are completed, automatically append to daily memory
Usage: Called by task management system or manually
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional


def append_task_completion(
    task_name: str,
    category: str = "progress",
    date: Optional[str] = None
) -> bool:
    """
    Append task completion to daily memory
    
    Args:
        task_name: Name of completed task
        category: Category (default: "progress")
        date: Date in YYYY-MM-DD format (default: today)
    
    Returns:
        True if successful, False otherwise
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    local_filename = f"{date}.json"
    local_dir = "data/memories"
    local_path = os.path.join(local_dir, local_filename)
    
    current_time = datetime.now().isoformat()
    
    try:
        # Load existing memory or create new
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                memory = json.load(f)
        else:
            os.makedirs(local_dir, exist_ok=True)
            memory = {
                "id": f"auto_{date}",
                "date": date,
                "entries": [],
                "combined_content": "",
                "created_at": current_time,
                "updated_at": current_time
            }
        
        # Append task completion entry
        task_entry = {
            "time": current_time,
            "content": f"✅ 完成: {task_name}",
            "ai_processed": None,
            "metadata": {
                "mood": 7,
                "focus": 8,
                "energy": 7,
                "tags": [category, "task_completion"],
                "is_ai": False,
                "ai_model": "None"
            }
        }
        
        memory["entries"].append(task_entry)
        memory["updated_at"] = current_time
        
        # Update combined content
        all_content = "\n\n---\n\n".join([
            entry.get("content", "") for entry in memory["entries"]
        ])
        memory["combined_content"] = all_content
        
        # Write back
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        
        # Use safe print for Windows console
        try:
            print(f"[OK] Task completion appended: {task_name} -> {local_path}")
        except UnicodeEncodeError:
            print(f"[OK] Task completion appended to {local_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to append task completion: {e}")
        return False


def watch_task_file(task_file_path: str = "task.md"):
    """
    Watch task.md for changes and auto-append completions
    (Future implementation - requires file watcher)
    """
    # TODO: Implement file watcher
    # When [x] is detected, extract task name and call append_task_completion()
    pass


# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python task_tracker.py 'Task Name' [category] [date]")
        sys.exit(1)
    
    task_name = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else "progress"
    date = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = append_task_completion(task_name, category, date)
    sys.exit(0 if success else 1)
