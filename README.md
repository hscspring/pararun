<div align="center">
  <img src="docs/images/pararun_banner.jpg" alt="Pararun Banner" width="100%">

  <br />

  <h1>🚀 Pararun</h1>

  <p><strong>The resilient concurrent executor for Python: Async, Parallel, and Threaded tasks with built-in idempotency.</strong></p>

  <p>
    <a href="https://pypi.org/project/pararun"><img src="https://img.shields.io/pypi/v/pararun?color=orange&style=flat-square" alt="PyPI"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License"></a>
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square" alt="Python Version">
  </p>

  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</div>

---

## 🌟 Overview

**Pararun** is a lightweight, fault-tolerant Python library for concurrent and parallel task execution. It simplifies running tasks using `asyncio`, `multiprocessing`, or `threading`, with built-in support for persistent caching (idempotency), progress bars, and streaming large datasets.

It solves a common real-world problem: **How to turn a "run-once-and-crash" script into a resumable, long-running task system without rewriting code?**

### ✨ Key Features

- 🚀 **Unified API**: Simple `pr.map` for parallel processing and `pr.aio_map` for async tasks.
- 💾 **Idempotent Caching**: Automatically skips processed items by checking a JSONL cache file. Perfect for resumable long-running jobs.
- 🌊 **Streaming Support**: Handles large datasets (generators) with controlled memory usage using backpressure.
- 📊 **Progress Monitoring**: Integrated `tqdm` progress bars.
- 🛡️ **Fault Tolerance**: Safely handles crashes by flushing results to disk periodically.

---

## 📦 Installation

```bash
pip install pararun
```

------

## ⚡ Quick Start

### 1. Parallel Processing (CPU/IO Bound)

Use `pr.map` for blocking functions. It handles both list and generator inputs.


```Python
import pararun as pr
import time

def process_file(filename):
    time.sleep(0.1)  # Simulate blocking work
    return {"id": filename, "status": "done"}

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

Use `pr.aio_map` for native async functions without breaking event loop semantics.


```Python
import pararun as pr
import asyncio

async def fetch_url(item):
    await asyncio.sleep(0.1) 
    return {"id": item["url"], "status": 200}

async def main():
    urls = [{"url": f"[https://example.com/](https://example.com/){i}"} for i in range(100)]
    
    await pr.aio_map(
        func=fetch_url,
        iterable=urls,
        n_workers=10,
        cache_path="async_results.jsonl"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

------

## 🛡️ Idempotency & Resuming

When `cache_path` is provided, Pararun ensures your work is never wasted:

- **Run 1**: Process 50% of items -> Unexpected Crash (OOM, Network, etc).
- **Run 2**: Point to the same `cache_path`. Pararun skips the finished 50% and resumes instantly.

By default, it uses the `"id"` field for deduplication. Customize it via `key_field`:


```Python
pr.map(..., cache_path="cache.jsonl", key_field="filename")
```

------

## 🌊 Memory-Safe Streaming

Pararun is designed for datasets that don't fit in memory. Using bounded queues (semaphores), it ensures that only a limited number of items (`n_workers * 2`) are held in memory, even if your generator produces millions of items.

------

## 📄 License

MIT © 2025