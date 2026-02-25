"""
Test Daily Reflection Agent
"""

import asyncio
from app.subconscious.daily_reflection import run_daily_reflection


async def test_reflection():
    print("=" * 60)
    print("Testing Daily Reflection Agent")
    print("=" * 60)
    
    # Test with today's date
    await run_daily_reflection("2026-02-17")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("Check: data/reflections/2026-02-17.md")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_reflection())
