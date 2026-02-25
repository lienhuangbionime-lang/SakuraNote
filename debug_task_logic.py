
import sys
import os
import asyncio

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend-cortex"))

from dotenv import load_dotenv
load_dotenv("backend-cortex/.env")

from app.core.database import supabase

async def test_completion():
    print("Testing Task Completion Logic...")
    
    # Get a task ID
    res = supabase.table("tasks").select("id").limit(1).execute()
    if not res.data:
        print("No tasks found to test.")
        return
        
    task_id = res.data[0]['id']
    print(f"Attempting to complete task: {task_id}")
    
    try:
        # 1. Update status
        print("Updating status to 'done'...")
        # Note: .select() is needed to return data in v2, but if it fails, try without
        update_res = supabase.table("tasks").update({"status": "done"}).eq("id", task_id).execute()
        print(f"Update Success: {len(update_res.data)} records updated.")
        
        # 2. Test the log insertion
        print("Testing log insertion...")
        entry = {
            "date": "2026-02-15",
            "content": f"- [x] TEST Completion of {task_id}",
            "category": "task_completion", # Schema: category, not type
            "is_ai": False,
            "tags": ["test"]
        }
        log_res = supabase.table("memories").insert(entry).execute()
        print(f"Log Success: {log_res.data}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_completion())
