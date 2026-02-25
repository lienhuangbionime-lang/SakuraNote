
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.workers.crystallize import crystallize_memories
import logging

router = APIRouter()
logger = logging.getLogger("cortex.api.crystallize")

@router.post("/crystallize")
async def trigger_crystallization(background_tasks: BackgroundTasks, days: int = 3):
    """
    Manually trigger the Crystallization Pipeline.
    Extracts Nodes & Edges from the last N days of memories.
    """
    logger.info(f"Received request to crystallize last {days} days.")
    
    # Run in background to avoid timeout
    background_tasks.add_task(crystallize_memories, days)
    
    return {"status": "accepted", "message": "Crystallization started in background."}
