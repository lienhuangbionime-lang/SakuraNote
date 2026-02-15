-- Enable the pgvector extension to work with embedding vectors
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a function to search for memories
-- [Aligned with User Schema] 3072 dimensions, returns metadata JSONB
CREATE OR REPLACE FUNCTION match_memories (
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
    -- Construct metadata object dynamically or use existing columns
    -- Since User Schema has flat columns, we build the object here to match the signature
    jsonb_build_object(
        'date', memories.date, 
        'tags', memories.tags, 
        'category', memories.category,
        'mood', memories.mood,
        'focus', memories.focus,
        'energy', memories.energy
    ) as metadata,
    1 - (memories.embedding <=> query_embedding) AS similarity
  FROM memories
  WHERE 1 - (memories.embedding <=> query_embedding) > match_threshold
  ORDER BY memories.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
