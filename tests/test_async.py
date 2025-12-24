
import pytest
import asyncio
import json

import pararun as pr


async def async_worker(item):
    await asyncio.sleep(0.01)
    return {"id": item["id"], "val": item["val"] * 2}


@pytest.fixture
def cache_path(tmp_path):
    return tmp_path / "cache.jsonl"


@pytest.mark.asyncio
async def test_simple_async_map(cache_path):
    items = [{"id": i, "val": i} for i in range(10)]
    
    await pr.aio_map(
        func=async_worker,
        iterable=items,
        n_workers=2,
        cache_path=str(cache_path),
        save_frequency=2
    )
    
    with open(cache_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 10
        data = [json.loads(line) for line in lines]
        # Verify data integrity
        ids = sorted([d["id"] for d in data])
        assert ids == list(range(10))


@pytest.mark.asyncio
async def test_idempotency(cache_path):
    # 1. Run first half
    items_1 = [{"id": i, "val": i} for i in range(5)]
    await pr.aio_map(async_worker, items_1, 2, str(cache_path))
    
    # 2. Run all (should skip first 5)
    items_all = [{"id": i, "val": i} for i in range(10)]
    await pr.aio_map(async_worker, items_all, 2, str(cache_path))
    
    with open(cache_path, "r") as f:
        lines = f.readlines()
        # If idempotency works, we should still only have 10 lines (5 unique from first run + 5 new)
        assert len(lines) == 10
