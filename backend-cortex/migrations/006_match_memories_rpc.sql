-- LifeOS v3.5 - Supabase RPC Function for Vector Search
-- Purpose: Enable hybrid search (semantic + metadata filters)
-- Usage: Called by app/services/rag.py::hybrid_search()

-- Create match_memories function for pgvector similarity search
CREATE OR REPLACE FUNCTION match_memories(
  query_embedding vector(3072),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    memories.id,
    memories.content,
    jsonb_build_object(
      'date', memories.date,
      'tags', memories.tags,
      'category', memories.category,
      'mood', memories.mood,
      'focus', memories.focus,
      'energy', memories.energy
    ) as metadata,
    1 - (memories.embedding <=> query_embedding) as similarity
  FROM memories
  WHERE 
    memories.embedding IS NOT NULL
    AND 1 - (memories.embedding <=> query_embedding) > match_threshold
  ORDER BY memories.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION match_memories TO authenticated;
GRANT EXECUTE ON FUNCTION match_memories TO anon;

-- Test the function (optional)
-- SELECT * FROM match_memories(
--   (SELECT embedding FROM memories LIMIT 1),
--   0.5,
--   5
-- );
