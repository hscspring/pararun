# Pararun：为脚本与长期任务而生的并发执行库

**Pararun** 是一个面向工程实践的 Python 并发执行库，用于**稳定、可恢复地运行大量任务**。
它专注解决一个在真实项目中反复出现、却长期被低估的问题：

> **如何在不重写代码、不引入复杂框架的前提下，把“跑一次就可能崩”的脚本，变成可中断、可恢复、可长期运行的任务系统？**

Pararun 不是为了追求极致吞吐，而是为了**让任务“跑得久、跑得稳、跑得省心”**。

---

## 适用场景

Pararun 尤其适合以下工作流：

* 数据处理 / 清洗 / 转换脚本
* 批量调用 API / 模型 / 推理服务
* 长时间运行、**可能中途失败**的任务
* 需要**断点续跑（幂等）**的实验或离线作业
* 使用 Python，但不想引入 Airflow / Ray / Celery 这类重量级系统

一句话概括：

> **Pararun 是“写给脚本作者的并发执行框架”。**

---

## 核心设计思想

### 1. 并发不是目的，**可恢复性才是**

在真实环境中，任务失败往往不是因为逻辑错误，而是因为：

* 机器重启
* 网络波动
* OOM / 超时
* 人为中断

Pararun 把“失败是常态”作为前提来设计：

* 每个任务结果都会**持续写入 JSONL 文件**
* 再次运行时，自动跳过已完成任务
* **不需要额外数据库，不需要额外配置**

这不是缓存优化，而是**幂等执行模型**。

---

### 2. 一个统一 API，覆盖三种并发模型

Pararun 并不强迫你选技术路线，而是根据任务性质自然分流：

* `pr.map`
  用于 **同步 / 阻塞函数**
  内部基于 `concurrent.futures`（线程 / 进程）

* `pr.aio_map`
  用于 **原生 async / asyncio 函数**
  不破坏 event loop 语义

你不需要为“并发方式”重写业务代码。

---

### 3. 天然支持“流式大数据集”

Pararun 从一开始就假设：

> 你的输入，可能大到**根本放不进内存**。

因此它支持：

* 直接传入 **生成器**
* 内部使用有界队列 / 信号量
* 自动反压（backpressure）
* 内存占用与 `n_workers` 成正比

即使你处理的是千万级任务，也不会“吃爆内存”。

---

### 4. 内建进度与可观测性

* 原生集成 `tqdm`
* 实时显示完成进度
* 非侵入式，不影响原有返回结构

你不需要再手写一堆进度统计逻辑。

---

## 快速开始

### 并发执行同步任务（CPU / IO）

```python
import pararun as pr
import time

def process_file(filename):
    time.sleep(0.1)
    return {"id": filename, "status": "done"}

files = (f"data_{i}.txt" for i in range(100))

pr.map(
    func=process_file,
    iterable=files,
    n_workers=4,
    cache_path="results.jsonl"
)
```

* 支持 list / generator
* 结果自动写入 `results.jsonl`
* 中断后可直接重跑

---

### 并发执行异步任务（AsyncIO）

```python
import pararun as pr
import asyncio

async def fetch_url(item):
    await asyncio.sleep(0.1)
    return {"id": item["url"], "status": 200}

async def main():
    urls = [{"url": f"https://example.com/{i}"} for i in range(100)]
    
    await pr.aio_map(
        func=fetch_url,
        iterable=urls,
        n_workers=10,
        cache_path="async_results.jsonl"
    )

asyncio.run(main())
```

---

## 幂等执行与断点续跑

只要指定 `cache_path`：

* Pararun 会自动读取已有结果
* 根据 `id`（或自定义字段）判断是否已处理
* **已完成任务不会再次执行**

```python
pr.map(
    ...,
    cache_path="cache.jsonl",
    key_field="filename"
)
```

典型使用方式：

* 第一次跑一半 → 程序中断
* 第二次直接重跑 → 自动从断点继续

---

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
