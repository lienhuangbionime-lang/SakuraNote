
import logging
import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

import google.generativeai as genai
from app.core.database import supabase
from app.core.gemini import get_model

logger = logging.getLogger("cortex.worker.crystallize")

SYSTEM_PROMPT = """
::: ROLE: THE LIBRARIAN (Knowledge Crystallizer) :::
You are the "Librarian" of the LifeOS. Your job is to read raw, messy diaries (Episodic Memory) and distill them into clean, structured Facts (Semantic Memory).

::: INPUT :::
A list of User Diaries (Content + Date).

::: OUTPUT :::
A JSON object containing:
1. "nodes": Distinct entities mentioned (People, Tools, Concepts, Projects).
2. "edges": Factual relationships between them.

::: RULES :::
1. **Nodes**:
   - Types: "person", "tool", "concept", "project", "location"
   - Label: Canonical name (e.g. "Tailwind", not "TailwindCSS" if previously used "Tailwind").
   - Extract ONLY significant entities. Ignore common words.

2. **Edges**:
   - Relation: Verb or preposition (e.g. "uses", "met_with", "working_on", "is_a").
   - Source/Target: Must match a Node Label.

3. **Projects**:
   - If the user clearly defines a project state change (e.g. "Started Project X"), extract it.

::: OUTPUT FORMAT :::
{
  "nodes": [
    {"label": "Tailwind CSS", "type": "tool"},
    {"label": "John", "type": "person"}
  ],
  "edges": [
    {"source": "LifeOS UI", "target": "Tailwind CSS", "relation": "uses"},
    {"source": "2026-02-15", "target": "John", "relation": "met_with"}
  ]
}
"""

async def crystallize_memories(days_back: int = 3):
    """
    Scans recent memories and extracts structured knowledge (Nodes/Edges).
    Idempotent: Uses Upsert to prevent duplicates.
    """
    logger.info(f"💎 Crystallization Worker Started (Window: {days_back} days)")
    
    # 1. Fetch Recent Memories
    target_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    try:
        # Fetch ID, Date, Content. Ignore empty content.
        res = supabase.table("memories").select("id, date, content").gte("date", target_date).neq("content", "").execute()
        memories = res.data or []
        
        if not memories:
            logger.info("No memories found to crystallize.")
            return {"status": "no_data"}
            
    except Exception as e:
        logger.error(f"Failed to fetch memories: {e}")
        return {"status": "error", "message": str(e)}

    # 2. Prepare AI Input
    memory_text = ""
    for m in memories:
        memory_text += f"\n--- Date: {m['date']} (ID: {m['id']}) ---\n{m['content']}\n"

    # 3. Call Gemini
    model_config = get_model("smart") # Use SMART model for high-quality extraction
    if not model_config["configured"]:
        return {"status": "skipped", "reason": "AI not configured"}
    
    try:
        model = genai.GenerativeModel(model_config["model"])
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\n::: EXAMINE THESE MEMORIES :::\n{memory_text}")
        
        # Parse JSON
        text = response.text.strip()
        # Extract JSON block if needed
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
        
        data = json.loads(text)
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        
        logger.info(f"💎 Extracted {len(nodes)} nodes and {len(edges)} edges.")
        
    except Exception as e:
        logger.error(f"AI Extraction Failed: {e}")
        return {"status": "error", "message": f"AI Error: {e}"}

    # 4. Upsert to Database
    # 4.1 Upsert Nodes
    upserted_nodes = 0
    for n in nodes:
        try:
            payload = {
                "label": n["label"],
                "type": n.get("type", "concept"),
                "metadata": {"source": "crystallizer", "last_seen": datetime.now().isoformat()}
            }
            # Handle collision (Label must be unique)
            # Supabase Upsert needs conflict target. Assuming Label is Unique or we query first.
            # Schema Registry says: "label": {"unique": true}
            
            # Upsert logic:
            supabase.table("nodes").upsert(payload, on_conflict="label").execute()
            upserted_nodes += 1
        except Exception as e:
            logger.warning(f"Node Upsert Failed ({n.get('label')}): {e}")

    # 4.2 Upsert Edges
    # We need UUIDs for Source/Target.
    # Map Label -> ID
    label_to_id = {}
    try:
        # Fetch all nodes (or just the ones we touched? All is safer for linking to old nodes)
        # optimization: Fetch valid labels from the batch
        all_labels = [n["label"] for n in nodes] 
        # Also need source/targets from edges if they weren't in nodes list (AI might generate edge to existing node)
        for e in edges:
            all_labels.append(e["source"])
            all_labels.append(e["target"])
        
        all_labels = list(set(all_labels))
        
        # Batch fetch IDs
        res = supabase.table("nodes").select("id, label").in_("label", all_labels).execute()
        for row in (res.data or []):
            label_to_id[row["label"]] = row["id"]
            
    except Exception as e:
        logger.error(f"ID Mapping Failed: {e}")

    upserted_edges = 0
    for e in edges:
        s_lbl = e.get("source")
        t_lbl = e.get("target")
        if s_lbl in label_to_id and t_lbl in label_to_id:
            try:
                payload = {
                    "source_id": label_to_id[s_lbl],
                    "target_id": label_to_id[t_lbl],
                    "relation": e.get("relation", "related"),
                    "weight": 1.0
                }
                # Edge constraints: source, target, relation unique?
                # Registry says: unique_edge: [source_id, target_id, relation]
                supabase.table("edges").upsert(payload, on_conflict="source_id,target_id,relation").execute()
                upserted_edges += 1
            except Exception as ex:
                logger.warning(f"Edge Upsert Failed: {ex}")
                
    return {
        "status": "success",
        "nodes_processed": upserted_nodes,
        "edges_processed": upserted_edges,
        "memories_scanned": len(memories)
    }
