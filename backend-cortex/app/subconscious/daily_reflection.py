"""
Daily Reflection Agent
Generates daily reflections from memory using Gemini
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)


REFLECTION_PROMPT = """
你是 LifeOS 的反思引擎。請根據今天的記憶生成一份深度反思報告。

# 今日記憶

{memory_content}

# 任務

請生成以下格式的反思報告：

## 📊 今日摘要
- 簡述今天的主要活動和成就

## 🎯 關鍵成就
- 列出 3-5 個最重要的完成事項

## 💡 學習與成長
- 今天學到了什麼？
- 有什麼新的洞察？

## 🔄 改進空間
- 哪些地方可以做得更好？
- 明天要注意什麼？

## 📝 明日計劃
- 基於今天的經驗，明天的重點是什麼？

請用繁體中文回答，保持簡潔但有深度。
"""


async def generate_daily_reflection(date: str) -> Optional[str]:
    """
    生成每日反思
    
    Args:
        date: YYYY-MM-DD format
    
    Returns:
        Reflection markdown content
    """
    try:
        # 1. 讀取當天記憶
        memory_file = f"data/memories/{date}.json"
        if not os.path.exists(memory_file):
            logger.warning(f"No memory file for {date}")
            return None
        
        with open(memory_file, "r", encoding="utf-8") as f:
            memory_data = json.load(f)
        
        memory_content = memory_data.get("combined_content", "")
        if not memory_content:
            logger.warning(f"Empty memory for {date}")
            return None
        
        logger.info(f"Loaded memory for {date}: {len(memory_content)} chars")
        
        # 2. 呼叫 Gemini 生成反思
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        prompt = REFLECTION_PROMPT.format(memory_content=memory_content)
        response = model.generate_content(prompt)
        
        reflection = response.text
        logger.info(f"Generated reflection for {date}: {len(reflection)} chars")
        
        return reflection
        
    except Exception as e:
        logger.error(f"Failed to generate reflection for {date}: {e}")
        return None


async def save_reflection(date: str, reflection: str) -> bool:
    """
    儲存反思報告
    
    Args:
        date: YYYY-MM-DD format
        reflection: Reflection content
    
    Returns:
        True if successful
    """
    try:
        # 建立目錄
        reflection_dir = "data/reflections"
        os.makedirs(reflection_dir, exist_ok=True)
        
        # 寫入檔案
        reflection_file = os.path.join(reflection_dir, f"{date}.md")
        with open(reflection_file, "w", encoding="utf-8") as f:
            f.write(f"# {date} Daily Reflection\n\n")
            f.write(reflection)
        
        logger.info(f"Saved reflection to {reflection_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save reflection for {date}: {e}")
        return False


async def run_daily_reflection(date: Optional[str] = None):
    """
    執行每日反思
    
    Args:
        date: YYYY-MM-DD format, defaults to today
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Starting daily reflection for {date}")
    
    # 生成反思
    reflection = await generate_daily_reflection(date)
    if not reflection:
        logger.error(f"Failed to generate reflection for {date}")
        return
    
    # 儲存反思
    success = await save_reflection(date, reflection)
    if success:
        logger.info(f"Daily reflection completed for {date}")
    else:
        logger.error(f"Failed to save reflection for {date}")


# CLI 測試
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 測試今天的反思
        await run_daily_reflection()
    
    asyncio.run(test())
