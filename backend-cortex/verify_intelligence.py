
import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from backend-cortex
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend-cortex'))

from app.core.vector import vector_engine
from app.core.database import supabase

async def verify():
    print("--- Intelligence Layer Verification ---")
    
    # 1. Test Embedding Generation
    print("[1] Testing Embedding Generation...")
    test_text = "Thales of Miletus: The first philosopher."
    embedding = vector_engine.get_embedding(test_text)
    
    if embedding and len(embedding) == 3072:
        print(f"  [OK] Generated embedding with {len(embedding)} dimensions.")
    else:
        print(f"  [FAIL] Embedding generation failed or wrong dimension. Got {len(embedding) if embedding else 'None'}")
        return

    # 2. Test Vector Search RPC
    print("[2] Testing Vector Search RPC...")
    try:
        # Search for similar content
        results = vector_engine.search_memories(supabase, test_text, limit=1)
        print(f"  [OK] RPC Call Successful. Returned {len(results)} results.")
        if results:
            print(f"    - Top Result: {results[0].get('content', 'N/A')[:50]}...")
            print(f"    - Metadata: {results[0].get('metadata')}")
    except Exception as e:
        print(f"  [FAIL] RPC Call Failed: {e}")
        return

    print("--- Verification Complete: Intelligence Layer Operational ---")

if __name__ == "__main__":
    load_dotenv("backend-cortex/.env")
    asyncio.run(verify())
