
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
import re
from app.core.database import supabase

router = APIRouter()
logger = logging.getLogger("cortex.brain")

@router.get("/graph")
async def get_brain_graph(limit: int = 500):
    """
    Generate the Neural Graph from memories.
    Replicates the logic of CoreEngine.parseGraphSeeds (Frontend) but on the backend.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        # 1. Fetch recent memories
        # We fetch only necessary fields to save bandwidth
        response = supabase.table("memories").select("id,date,content,tags,mood,focus,energy").order("date", desc=True).limit(limit).execute()
        memories = response.data or []

        nodes = {}
        links = {}

        def add_node(id, group, val, raw=None):
            if id not in nodes:
                nodes[id] = {"id": id, "group": group, "val": val}
                if raw:
                    nodes[id]["raw"] = raw

        def add_link(source, target, value):
            key = f"{source}-{target}"
            if key not in links:
                links[key] = {"source": source, "target": target, "value": value}
            else:
                links[key]["value"] += value

        # 2. Process Memories
        for memory in memories:
            date_id = memory.get("date")
            content = memory.get("content") or ""
            db_tags = memory.get("tags") or []
            
            if not date_id:
                continue

            # --- Nodes: Log Entry (Date) ---
            # Group 1 = Log
            add_node(date_id, 1, 5, raw=memory)

            # --- Extract Entities from Content ---
            
            # 1. Tags (#hashtag)
            # Regex: # followed by word chars, chinese, dot, dash
            tag_matches = re.findall(r'#([\w\u4e00-\u9fa5.-]+)', content)
            unique_tags = set(tag_matches)
            
            # Merge with DB tags
            for t in db_tags:
                unique_tags.add(t.replace("#", ""))
            
            # 2. Mentions (@name)
            mention_matches = re.findall(r'@([\w\u4e00-\u9fa5.-]+)', content)
            unique_mentions = set(mention_matches)
            
            # 3. Wiki Links ([[Link]])
            wiki_matches = re.findall(r'\[\[(.*?)\]\]', content)
            unique_wikis = set(wiki_matches)

            # --- Nodes & Links: Tags ---
            processed_tags = list(unique_tags)
            for tag in processed_tags:
                add_node(tag, 'tag', 3)
                add_link(date_id, tag, 1)

            # --- Nodes & Links: Mentions ---
            for person in unique_mentions:
                add_node(person, 'person', 5)
                add_link(date_id, person, 2)

            # --- Nodes & Links: Concepts ---
            for concept in unique_wikis:
                add_node(concept, 'concept', 4)
                add_link(date_id, concept, 2)

            # --- Co-occurrence (Tag <-> Tag) ---
            # Link tags that appear in the same entry
            for i in range(len(processed_tags)):
                for j in range(i + 1, len(processed_tags)):
                    t1 = processed_tags[i]
                    t2 = processed_tags[j]
                    # Sort to ensure consistent key
                    source, target = sorted([t1, t2])
                    add_link(source, target, 0.2)

        # 3. Format Output
        return {
            "nodes": list(nodes.values()),
            "links": list(links.values())
        }

    except Exception as e:
        logger.error(f"Graph Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
