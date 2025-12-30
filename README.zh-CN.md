<div align="center">
  <img src="docs/images/pararun_banner.jpg" alt="Pararun 架构图" width="100%">


  <br />

  <h1>🚀 Pararun</h1>

  <p><strong>为脚本和长期任务而生的并发执行库：支持 Async、多进程、多线程及内置断点续传。</strong></p>

  <p>
    <a href="https://pypi.org/project/pararun"><img src="https://img.shields.io/pypi/v/pararun?color=orange&style=flat-square" alt="PyPI"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/许可证-MIT-yellow.svg?style=flat-square" alt="License"></a>
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square" alt="Python 版本">
  </p>

  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</div>

---

## 🌟 项目定位

**Pararun** 是一个面向工程实践的 Python 并发执行库，旨在解决一个核心痛点：

> **如何在不引入复杂框架的前提下，把“跑一次就可能崩”的脚本，变成可中断、可恢复、可长期运行的任务系统？**

Pararun 不盲目追求极致吞吐量，它的核心价值在于让任务 **“跑得久、跑得稳、跑得省心”**。

---

## ✨ 核心设计思想

### 1. 并发不是目的，可恢复性才是 🛡️
在真实环境中，任务失败是常态。Pararun 采用 **“幂等执行模型”**：
* 结果实时持久化到 JSONL 文件。
* 再次运行时自动跳过已完成任务，无需数据库。
* **断点续跑**：如果程序中途崩溃，只需重新运行，它会从上次中断的地方继续。

### 2. 统一 API，覆盖多种并发模型 🚀
不需要为不同的并发方式重写业务代码：
* `pr.map`: 用于同步/阻塞函数（基于线程/进程池）。
* `pr.aio_map`: 用于原生 `asyncio` 异步函数。

### 3. 天然支持“流式大数据集” 🌊
Pararun 假设你的输入可能大到放不进内存。通过 **“反压（Backpressure）”** 机制，即使处理千万级 generator 任务，内存占用也始终与 `n_workers` 成正比，不会撑爆服务器。

### 4. 内建进度显示 📊
原生集成 `tqdm`，实时观测执行进度，无需手动编写统计逻辑。

---

## ⚡ 快速开始

### 并发执行同步任务 (CPU / IO)

```python
import pararun as pr
import time

def process_file(filename):
    time.sleep(0.1) # 模拟阻塞工作
    return {"id": filename, "status": "done"}

files = (f"data_{i}.txt" for i in range(100))

# 结果将自动写入并同步至 results.jsonl
pr.map(
    func=process_file,
    iterable=files,
    n_workers=4,
    cache_path="results.jsonl"
)
```

### 并发执行异步任务 (AsyncIO)


```Python
import pararun as pr
import asyncio

async def fetch_url(item):
    await asyncio.sleep(0.1)
    return {"id": item["url"], "status": 200}

async def main():
    urls = [{"url": f"[https://example.com/](https://example.com/){i}"} for i in range(100)]
    await pr.aio_map(fetch_url, urls, n_workers=10, cache_path="async_results.jsonl")

asyncio.run(main())
```

## 🛠️ 适用场景

- 数据工程：清洗、转换大规模离线数据。
- AI 工程：批量调用模型推理接口、下载海量训练素材。
- 运维脚本：对成千上万台机器进行异步巡检。
- 实验作业：需要记录中间结果并支持随时中断恢复的科研任务。


## 📄 许可证

MIT