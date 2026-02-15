from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import json
import uuid
import datetime

from app.core.gemini import get_model
from app.core.database import supabase

router = APIRouter()
logger = logging.getLogger("cortex.crystallize")

# --- Models ---

class Message(BaseModel):
    role: str
    content: str

class CrystallizeRequest(BaseModel):
    messages: List[Message]
    project_id: Optional[str] = None
    project_name: Optional[str] = None  # Used for generating Tags

# --- System Prompt ---

CRYSTALLIZER_SYSTEM_PROMPT = """
::: SYSTEM: THOUGHT CRYSTALLIZER :::

你現在是 LifeOS 的「思維結晶引擎」。
使用者剛結束了一場與 AI 的深度對話。你的任務不是繼續對話，而是「提取價值」。

# 輸入
一段包含使用者與 AI 的對話紀錄 (JSON list)。

# 輸出指令
請忽略所有的寒暄、重複確認、除錯過程。只保留：
1. **Title**: 給這場對話一個精確的標題 (10字以內)。
2. **Core Insights**: 對話中產生的核心概念、哲學或架構決定 (最多 3 點)。
3. **Next Actions**: 明確的下一步行動指令 (Todo List)。

# 輸出格式 (JSON Only)
{
  "title": "LifeOS 架構重構決策",
  "insights_markdown": "- 決定採用 FastAPI 作為神經中樞...\n- 放棄直接寫入 Project 的想法，改用掛載模式...",
  "actions_markdown": "- [ ] 建立 /crystallize API 端點\n- [ ] 更新 ContextModal 前端 UI"
}
"""

@router.post("/crystallize")
async def crystallize_thought(request: CrystallizeRequest):
    """
    Convert conversation history into a structured note (Memory) and link it to a Project or Inbox.
    """
    logger.info(f"🔮 Crystallizing thought sequence (messages: {len(request.messages)})...")
    
    try:
        # 1. Initialize Gemini
        # We need to import genai here because get_model doesn't return the client instance
        import google.generativeai as genai
        
        model_config = get_model("smart")
        
        if not model_config.get("configured"):
            raise HTTPException(status_code=503, detail="AI Service not configured (API Key missing)")
            
        model_name = model_config.get("model", "gemini-pro-latest")
        model = genai.GenerativeModel(model_name)
        
        # 2. Construct Prompt
        # Format conversation history for the model
        conversation_text = ""
        for msg in request.messages:
            role = msg.role.upper()
            content = msg.content
            conversation_text += f"[{role}]: {content}\n\n"
            
        full_prompt = f"{CRYSTALLIZER_SYSTEM_PROMPT}\n\n# Conversation Log:\n{conversation_text}\n\nPlease generate the JSON output."
        
        # 3. Call LLM
        response = model.generate_content(full_prompt)
        text = response.text.strip()
        
        # 4. Parse JSON
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
            
        try:
            structured_insight = json.loads(text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from AI response: {text}")
            raise HTTPException(status_code=500, detail="AI failed to generate valid JSON")

        # 5. Format Final Content (Markdown)
        final_content = f"""
# 🧠 Cortex Session: {structured_insight.get('title', 'Untitled Session')}

## 💡 Key Insights
{structured_insight.get('insights_markdown', '')}

## 🚀 Actionable Items
{structured_insight.get('actions_markdown', '')}

---
*Source: ContextModal Conversation*
"""

        # 6. Prepare Tags
        tags = ["cortex_session", "insight"]
        if request.project_name:
            # Normalize tag: lowercase, replace spaces with underscores if needed
            safe_project_tag = request.project_name.lower().replace(" ", "_")
            tags.append(safe_project_tag)
            
        # 7. Write to Supabase (Memories/LogEntry table??)
        # The user said "memories" table, but previous context used "LogEntry". 
        # registry.json mentions "memories" as the v3.5 name, but existing code uses "LogEntry".
        # I will check if "memories" table exists or if I should use "LogEntry".
        # Given the "Soul Alignment" objective, "memories" is the target, but current ingest.py falls back if schema mismatch.
        # I will try to insert into "memories" first (if the user migrated), if fails, fall back to "LogEntry".
        # Actually, let's stick to what's likely working: "LogEntry" based on ingest.py logs.
        # But wait, the user's specific instruction say: "API->>DB: INSERT into memories".
        # I will try "memories" and catch error to fallback to "LogEntry".
        
        # DB Payload
        db_payload = {
            "id": str(uuid.uuid4()),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"), # Today's date
            "content": final_content,
            "mood": 5, # Default neutral
            "focus": 5,
            "energy": 5,
            "tags": tags,
            "isAi": True,
            "aiModel": model_name,
            "meta": {
                "type": "crystallization",
                "source_project_id": request.project_id,
                "title": structured_insight.get('title')
            },
            "updatedAt": datetime.datetime.now().isoformat()
        }
        
        target_table = "memories" 
        
        if supabase:
            try:
                # Try inserting into 'memories' first
                res = supabase.table(target_table).insert(db_payload).execute()
                logger.info(f"✅ Crystallized thought stored in {target_table}.")
            except Exception as e:
                logger.warning(f"⚠️ Failed to write to '{target_table}', trying 'LogEntry' fallback. Error: {e}")
                target_table = "LogEntry"
                try:
                    # Adjust payload if needed for LogEntry (remove extra fields if strict?)
                    # Assuming LogEntry is the physical table in use
                    res = supabase.table(target_table).insert(db_payload).execute()
                    logger.info(f"✅ Crystallized thought stored in {target_table}.")
                except Exception as e2:
                    logger.error(f"❌ Database Write Failed: {e2}")
                    raise HTTPException(status_code=500, detail=f"Database error: {str(e2)}")
        else:
             logger.warning("Supabase not configured, cannot save memory.")
             raise HTTPException(status_code=503, detail="Database not available")

        return {"status": "success", "id": db_payload['id'], "table": target_table}

    except Exception as e:
        logger.error(f"Crystallization Failed: {str(e)}")
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
