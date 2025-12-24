
import asyncio
import json
import random
from pathlib import Path
import sys

# Ensure pararun is in path
sys.path.append(str(Path(__file__).parent.parent))

import pararun as pr

async def process_item(item):
    await asyncio.sleep(0.01)
    # Simulate work
    res = {"id": item["id"], "output": item["id"] ** 2}
    return res

async def main():
    # 1. Generate dummy data
    items = [{"id": i, "value": random.random()} for i in range(100)]
    
    print(f"Generated {len(items)} items. Running pararun...")

    # 2. Run pararun
    # Note: cache_path will auto-save results
    await pr.aio_map(
        func=process_item,
        iterable=items,
        n_workers=10,
        cache_path="examples/cache_async.jsonl",
        save_frequency=10
    )
    
    print("Done. Checking cache...")
    
    # 3. Verify cache
    with open("examples/cache_async.jsonl", "r") as f:
        lines = f.readlines()
        print(f"Cache has {len(lines)} lines.")
        assert len(lines) == 100

if __name__ == "__main__":
    asyncio.run(main())
