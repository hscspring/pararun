# Pararun

**Pararun** is a lightweight, fault-tolerant Python library for concurrent and parallel task execution. It simplifies running tasks using `asyncio`, `multiprocessing`, or `threading`, with built-in support for persistent caching (idempotency), progress bars, and streaming large datasets.

## Features

- 🚀 **Unified API**: Simple `pr.map` for parallel processing and `pr.aio_map` for async tasks.
- 💾 **Idempotent Caching**: Automatically skips processed items by checking a JSONL cache file. Perfect for resumable long-running jobs.
- 🌊 **Streaming Support**: Handles large datasets (generators) with controlled memory usage using backpressure.
- 📊 **Progress Monitoring**: Integrated `tqdm` progress bars.
- 🛡️ **Fault Tolerance**: Safely handles crashes by flushing results to disk periodically.

## Installation

```bash
pip install pararun
```

## Quick Start

### 1. Parallel Processing (CPU/IO Bound)

Use `pr.map` for blocking functions. It uses `concurrent.futures` implementation.

```python
import pararun as pr
import time

def process_file(filename):
    time.sleep(0.1)  # Simulate blocking work
    return {"id": filename, "status": "done"}

# Works with Lists or Generators
files = (f"data_{i}.txt" for i in range(100))

# Result is saved to 'results.jsonl' automatically
pr.map(
    func=process_file,
    iterable=files,
    n_workers=4,
    cache_path="results.jsonl"
)
```

### 2. Async Processing (AsyncIO)

Use `pr.aio_map` for native async functions.

```python
import pararun as pr
import asyncio

async def fetch_url(item):
    await asyncio.sleep(0.1) # Simulate network request
    return {"id": item["url"], "status": 200}

async def main():
    urls = [{"url": f"https://example.com/{i}"} for i in range(100)]
    
    await pr.aio_map(
        func=fetch_url,
        iterable=urls,
        n_workers=10,
        cache_path="async_results.jsonl"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Idempotency & Resuming
When `cache_path` is provided, `pararun` reads the file (if it exists) to verify which items have already been processed. 

By default, it assumes the output items contain an `"id"` field. You can customize this field using the `key_field` parameter:

```python
pr.map(..., cache_path="cache.jsonl", key_field="filename")
```

- **Run 1**: Process 50% of items -> Crash.
- **Run 2**: Point to same `cache_path`. `pararun` skips the first 50% and resumes from where it left off.

### Streaming Large Datasets
`pararun` is designed to be memory efficient. It uses bounded queues (semaphores) to ensure that even if you pass a generator with 100M items, only `n_workers * 2` items are held in memory at any time.

## Development

Install dependencies and run tests:

```bash
# Install package in editable mode
pip install -e .

# Run tests
python -m pytest
```

## License

MIT
