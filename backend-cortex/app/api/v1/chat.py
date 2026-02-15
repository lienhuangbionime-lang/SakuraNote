
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import json
import asyncio
from app.core.gemini import get_model
import google.generativeai as genai

router = APIRouter()
logger = logging.getLogger("cortex.chat")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    model: Optional[str] = "gemini-2.0-pro-exp-02-05"

SYSTEM_PROMPT = """
You are Cortex, the digital extension of the user's mind (LifeOS).
Your goal is to help the user manage their projects, clarify their thoughts, and retrieve memories.
- Be concise, direct, and insightful.
- Use Markdown for formatting.
- If the user asks about their data, you should query the memory bank (though this capability is simulated for now).
- Maintain a "Glass Box" philosophy: explain your reasoning if asked.
"""

@router.post("/message")
async def chat_message(request: ChatRequest):
    """
    Streaming Chat Endpoint
    """
    logger.info(f"💬 Chat Request: {request.message}")
    
    try:
        model_config = get_model("smart")
        if not model_config.get("configured"):
             raise HTTPException(status_code=503, detail="Cortex AI not configured (API Key missing)")

        model_name = request.model or model_config.get("model")
        model = genai.GenerativeModel(model_name)
        
        # Convert history to Gemini format
        chat_history = []
        # Add System Prompt as the first part of context if possible, 
        # or just prepend to the first user message. 
        # Gemini Python SDK handles history differently (start_chat).
        
        # Simple approach: Construct a full prompt or use start_chat
        gemini_history = []
        for msg in request.history:
             role = "user" if msg.role == "user" else "model"
             gemini_history.append({"role": role, "parts": [msg.content]})
             
        chat = model.start_chat(history=gemini_history)
        
        async def event_generator():
            try:
                # Send message with streaming
                # We prepend system prompt to the user message for now as a soft system instruction
                full_input = f"{SYSTEM_PROMPT}\n\nUser: {request.message}"
                
                response = await chat.send_message_async(full_input, stream=True)
                
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
                        
            except Exception as e:
                logger.error(f"Stream Error: {e}")
                yield f"\n\n[System Error: {str(e)}]"

        return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
