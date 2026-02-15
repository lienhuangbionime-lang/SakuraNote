# app/api/v1/memories.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import asyncio

from app.models.schemas import LogEntrySchema
from app.core.database import supabase
from app.core.vector import vector_engine

router = APIRouter()
logger = logging.getLogger("app.api.v1.memories")


@router.get("/", response_model=List[LogEntrySchema])
async def get_recent_memories(
    limit: int = 20,
    q: Optional[str] = Query(None, description="Search query (semantic or keyword)")
):
    """
    Retrieve memories.
    - If `q` is provided: Performs Semantic Search (Vector).
    - If `q` is None: Returns recent memories (Chronological).
    """
    if supabase is None:
        logger.warning("Supabase client unavailable; cannot fetch memories.")
        raise HTTPException(status_code=503, detail="Database unavailable (supabase not configured).")

    try:
        # Case 1: Semantic Search
        if q and len(q.strip()) > 0:
            # Run vector search in thread pool
            def vector_search():
                results = vector_engine.search_memories(supabase, q, limit=limit)
                
                # [Schema Alignment]
                # RPC returns {id, content, metadata(json), similarity}
                # Pydantic expects flat {id, content, date, tags, mood...}
                mapped_results = []
                for row in results:
                    meta = row.get("metadata", {}) or {}
                    mapped_results.append({
                        "id": row.get("id"),
                        "content": row.get("content"),
                        "date": meta.get("date"),
                        "tags": meta.get("tags", []),
                        "category": meta.get("category"),
                        "mood": meta.get("mood", 5),
                        "focus": meta.get("focus", 5),
                        "energy": meta.get("energy", 5),
                        "is_ai": False, # Default for search results if not in metadata
                        "ai_model": None
                    })
                return mapped_results
            
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, vector_search)
            return data

        # Case 2: Recent Memories (Chronological)
        # supabase client is sync; run in thread to avoid blocking event loop
        def query():
            try:
                result = supabase.table("memories").select("*").order("date", desc=True).limit(limit).execute()
                return result
            except Exception as e:
                # bubble up
                raise

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, query)

        # supabase-py returns a dict-like object with 'data' and 'error'
        data = getattr(result, "data", None) or result.get("data") if isinstance(result, dict) else None
        error = getattr(result, "error", None) or result.get("error") if isinstance(result, dict) else None

        if error:
            logger.error("Supabase error while fetching memories: %s", error)
            raise HTTPException(status_code=500, detail="Database query error")

        return data or []

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error fetching memories: %s", e)
        raise HTTPException(status_code=500, detail="Unexpected error fetching memories")