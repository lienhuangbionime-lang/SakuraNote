
import asyncio
import os
import time
from typing import List, Dict, Any
from app.core.vector import VectorEngine
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class EmbeddingWorker:
    """
    Subconscious Worker (Option A)
    Runs in the background to process memories that lack embeddings.
    """
    
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL")
        self.key: str = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.url, self.key)
        self.vector_engine = VectorEngine()
        self.batch_size = 5
        self.sleep_interval = 60 # Check every 60 seconds
        self.is_running = False

    async def start(self):
        """Starts the worker loop."""
        self.is_running = True
        print("[Subconscious] Worker started. Monitoring null embeddings...")
        while self.is_running:
            try:
                await self.process_batch()
            except Exception as e:
                print(f"[Subconscious] Error in worker loop: {e}")
            
            await asyncio.sleep(self.sleep_interval)

    async def process_batch(self):
        """
        Fetches memories with embedding IS NULL and generates them.
        """
        # 1. Fetch
        response = self.supabase.table("memories")\
            .select("id, content")\
            .is_("embedding", "null")\
            .limit(self.batch_size)\
            .execute()
        
        memories = response.data
        if not memories:
            return # Nothing to do

        print(f"[Subconscious] Processing {len(memories)} memories...")

        for memory in memories:
            content = memory.get("content", "")
            if not content:
                continue
                
            # 2. Generate
            embedding = self.vector_engine.get_embedding(content)
            
            if embedding:
                # 3. Update
                try:
                    self.supabase.table("memories")\
                        .update({"embedding": embedding})\
                        .eq("id", memory["id"])\
                        .execute()
                    print(f"  -> Embedded: {memory['id']}")
                except Exception as e:
                    print(f"  -> Failed to update {memory['id']}: {e}")
            else:
                print(f"  -> Failed to generate embedding for {memory['id']}")

        print("[Subconscious] Batch complete.")

# Global instance
embedding_worker = EmbeddingWorker()
