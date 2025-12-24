
import pytest
import json
import time


import pararun as pr


def sync_worker(item):
    time.sleep(0.001)
    return {"id": item, "val": item * 2}


def sync_worker_dict(item):
    return {"id": item["id"], "val": item["val"] + 1}


@pytest.fixture
def cache_path(tmp_path):
    return tmp_path / "cache_sync.jsonl"

def test_process_map(cache_path):
    items = list(range(20))
    pr.map(
        func=sync_worker,
        iterable=items,
        n_workers=2,
        backend="process",
        cache_path=str(cache_path)
    )
    
    with open(cache_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 20


def test_streaming_generator(cache_path):
    def gen():
        for i in range(20):
            yield {"id": i, "val": i}
    
    pr.map(
        func=sync_worker_dict,
        iterable=gen(),
        n_workers=2,
        cache_path=str(cache_path),
        save_frequency=5
    )
        
    with open(cache_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 20

def test_idempotency(cache_path):
    # Pre-populate cache manually
    with open(cache_path, "w") as f:
        f.write(json.dumps({"id": 0, "val": 0}) + "\n")
        f.write(json.dumps({"id": 1, "val": 2}) + "\n")
        
    items = [{"id": i, "val": i} for i in range(5)]
    
    pr.map(
        func=sync_worker_dict, 
        iterable=items, 
        n_workers=2, 
        backend="process", 
        cache_path=str(cache_path)
    )
    
    with open(cache_path, "r") as f:
        lines = f.readlines()
        # 2 existing + 3 new = 5 total lines (no duplicates)
        assert len(lines) == 5
