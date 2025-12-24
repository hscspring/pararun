
import time
import sys
from pathlib import Path
import random
import json

# Ensure pararun is in path
sys.path.append(str(Path(__file__).parent.parent))

import pararun as pr

def process_file_mock(filename):
    # Simulate processing a file
    time.sleep(0.01)
    # Return some result
    return {"filename": filename, "count": random.randint(1, 100)}

def main():
    # 1. Generate dummy filenames (as generator)
    def file_generator():
        for i in range(50):
            yield f"file_{i}.parquet"

    print(f"Processing 50 files with parallel processes...")

    # 2. Run pararun
    pr.map(
        func=process_file_mock,
        iterable=file_generator(),
        n_workers=4,
        backend="process",
        cache_path="examples/cache_mp.jsonl",
        key_field="filename",
        save_frequency=10
    )

    print("Done. Checking cache...")
    
    # 3. Verify cache
    with open("examples/cache_mp.jsonl", "r") as f:
        lines = f.readlines()
        print(f"Cache has {len(lines)} lines.")
        assert len(lines) == 50

if __name__ == "__main__":
    main()
