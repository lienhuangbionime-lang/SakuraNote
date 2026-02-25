"""
Test Script for Local-First Storage Architecture
Purpose: Verify that ingest writes locally and RAG reads from local files
Usage: python tools/test_local_storage.py
"""

import asyncio
import os
import json
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag import hybrid_search, load_local_memory


async def test_local_storage():
    print("=" * 60)
    print("Local-First Storage Architecture Test")
    print("=" * 60)
    
    # Test 1: Check if data directory exists
    print("\n[Test 1] Checking data/memories directory...")
    data_dir = "data/memories"
    if os.path.exists(data_dir):
        print(f"✅ Directory exists: {data_dir}")
        files = os.listdir(data_dir)
        print(f"   Found {len(files)} local memory files")
        for f in files[:5]:  # Show first 5
            print(f"   - {f}")
    else:
        print(f"❌ Directory not found: {data_dir}")
        return
    
    # Test 2: Test load_local_memory function
    print("\n[Test 2] Testing load_local_memory()...")
    if files:
        test_file = files[0]
        content = load_local_memory(test_file)
        if content:
            print(f"✅ Successfully loaded: {test_file}")
            print(f"   Content preview: {content[:100]}...")
        else:
            print(f"❌ Failed to load: {test_file}")
    else:
        print("⚠️  No files to test")
    
    # Test 3: Test hybrid_search (requires Supabase)
    print("\n[Test 3] Testing hybrid_search()...")
    try:
        results = await hybrid_search(
            query="投資決策",
            limit=3,
            similarity_threshold=0.5
        )
        if results:
            print(f"✅ Found {len(results)} relevant memories")
            for i, mem in enumerate(results, 1):
                print(f"   Memory {i}:")
                print(f"     - Date: {mem.date}")
                print(f"     - Similarity: {mem.similarity:.2f}")
                print(f"     - Content: {mem.content[:80]}...")
        else:
            print("⚠️  No memories found (this is OK if database is empty)")
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
    
    # Test 4: Verify local file structure
    print("\n[Test 4] Verifying local file structure...")
    if files:
        test_file_path = os.path.join(data_dir, files[0])
        with open(test_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_fields = ["id", "date", "content", "metadata"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if not missing_fields:
            print(f"✅ File structure valid")
            print(f"   Fields: {list(data.keys())}")
        else:
            print(f"❌ Missing fields: {missing_fields}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_local_storage())
