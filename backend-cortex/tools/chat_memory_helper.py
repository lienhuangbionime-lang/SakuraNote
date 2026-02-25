"""
Chat Memory Injection - Let AI read its memory during conversation
"""

from typing import List, Dict
from tools.ai_memory_reader import (
    read_daily_memory,
    read_monthly_review,
    read_recent_memories,
    search_memories_by_tag,
    get_knowledge_graph
)


async def inject_memory_context(user_query: str) -> str:
    """
    根據使用者問題，自動注入相關記憶
    
    Args:
        user_query: 使用者問題
    
    Returns:
        Formatted context string
    """
    context_parts = []
    
    # 檢測日期查詢
    if "今天" in user_query or "今日" in user_query:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        memory = await read_daily_memory(today)
        if memory:
            context_parts.append(f"## 今日記憶\n{memory.get('local', {}).get('combined_content', '')}")
    
    # 檢測月度查詢
    if "本月" in user_query or "這個月" in user_query:
        from datetime import datetime
        now = datetime.now()
        review = await read_monthly_review(now.year, now.month)
        if review:
            context_parts.append(f"## 本月總結\n{review.get('summary', '')}")
    
    # 檢測最近記憶
    if "最近" in user_query:
        recent = await read_recent_memories(7)
        if recent:
            recent_text = "\n".join([f"- {m['date']}: {m.get('ai_insights', '')[:100]}" for m in recent[:5]])
            context_parts.append(f"## 最近記憶\n{recent_text}")
    
    # 檢測知識查詢（RAG, embedder, etc.）
    keywords = ["RAG", "embedder", "向量", "Supabase", "Gemini"]
    for keyword in keywords:
        if keyword in user_query:
            graph = await get_knowledge_graph(keyword)
            if graph:
                context_parts.append(f"## {keyword} 相關知識\n{graph.get('node', {}).get('description', '')}")
    
    # 組合 context
    if context_parts:
        return "\n\n---\n\n".join(context_parts)
    
    return ""


# 範例使用
async def example():
    query = "今天做了什麼？"
    context = await inject_memory_context(query)
    print(f"Context for '{query}':\n{context}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())
