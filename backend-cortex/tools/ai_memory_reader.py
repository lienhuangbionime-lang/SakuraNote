"""
AI Memory Reading Tools
Purpose: Let AI read its own memory from database and local files
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from app.core.database import supabase

def get_supabase():
    return supabase


async def read_daily_memory(date: str) -> Optional[Dict]:
    """
    讀取特定日期的完整記憶
    
    Args:
        date: YYYY-MM-DD format
    
    Returns:
        {
            "local": {...},      # 本地完整 Markdown
            "supabase": {...}    # Supabase 精簡版
        }
    """
    result = {}
    
    # 1. 讀取本地完整版
    local_path = f"data/memories/{date}.json"
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            result["local"] = json.load(f)
    
    # 2. 讀取 Supabase 精簡版
    supabase = get_supabase()
    if supabase:
        response = supabase.table("memories").select("*").eq("date", date).execute()
        if response.data:
            result["supabase"] = response.data[0]
    
    return result if result else None


async def read_monthly_review(year: int, month: int) -> Optional[Dict]:
    """
    讀取月度總結
    
    Args:
        year: 2026
        month: 2
    
    Returns:
        Monthly review data
    """
    supabase = get_supabase()
    if not supabase:
        return None
    
    response = supabase.table("MonthlyReview").select("*").eq("year", year).eq("month", month).execute()
    
    return response.data[0] if response.data else None


async def read_recent_memories(days: int = 7) -> List[Dict]:
    """
    讀取最近 N 天的記憶
    
    Args:
        days: 天數
    
    Returns:
        List of memories
    """
    supabase = get_supabase()
    if not supabase:
        return []
    
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    response = supabase.table("memories").select("*").gte("date", start_date).order("date", desc=True).execute()
    
    return response.data


async def search_memories_by_tag(tag: str) -> List[Dict]:
    """
    根據標籤搜尋記憶
    
    Args:
        tag: 標籤名稱
    
    Returns:
        List of memories
    """
    supabase = get_supabase()
    if not supabase:
        return []
    
    response = supabase.table("memories").select("*").contains("tags", [tag]).execute()
    
    return response.data


async def get_knowledge_graph(node_name: str) -> Dict:
    """
    查詢知識圖譜
    
    Args:
        node_name: 節點名稱（如 "RAG"）
    
    Returns:
        {
            "node": {...},
            "related_nodes": [...]
        }
    """
    supabase = get_supabase()
    if not supabase:
        return {}
    
    # 查詢節點
    node_response = supabase.table("nodes").select("*").ilike("name", f"%{node_name}%").execute()
    
    if not node_response.data:
        return {}
    
    node = node_response.data[0]
    node_id = node["id"]
    
    # 查詢相關連線
    edges_response = supabase.table("edges").select("*, source:nodes!edges_source_id_fkey(*), target:nodes!edges_target_id_fkey(*)").or_(f"source_id.eq.{node_id},target_id.eq.{node_id}").execute()
    
    return {
        "node": node,
        "edges": edges_response.data
    }


async def get_active_tasks() -> List[Dict]:
    """
    查詢進行中的任務
    
    Returns:
        List of active tasks
    """
    supabase = get_supabase()
    if not supabase:
        return []
    
    response = supabase.table("tasks").select("*").eq("status", "in_progress").execute()
    
    return response.data


# CLI 測試
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 測試讀取今日記憶
        today = datetime.now().strftime("%Y-%m-%d")
        memory = await read_daily_memory(today)
        print(f"Today's memory: {memory}")
        
        # 測試讀取月度總結
        review = await read_monthly_review(2026, 2)
        print(f"Monthly review: {review}")
        
        # 測試搜尋標籤
        rag_memories = await search_memories_by_tag("RAG")
        print(f"RAG memories: {len(rag_memories)}")
    
    asyncio.run(test())
