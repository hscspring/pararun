from typing import Callable, Iterable, Any, Optional, Union, AsyncIterable

from .async_run import AsyncRunner
from .executor_run import ExecutorRunner
from .store import JsonlStore


def map(
    func: Callable[[Any], Any],
    iterable: Iterable[Any],
    n_workers: int = 4,
    backend: str = "process",  # "process" or "thread"
    cache_path: Optional[str] = None,
    key_field: str = "id",
    save_frequency: int = 1000,
    total: Optional[int] = None
):
    """
    Parallel map using concurrent.futures (ProcessPoolExecutor or ThreadPoolExecutor).
    """
    store = None
    if cache_path:
        store = JsonlStore(path=cache_path, key_field=key_field, flush_interval=save_frequency)

    runner = ExecutorRunner(
        func=func, 
        n_workers=n_workers, 
        executor_type=backend,
        store=store
    )
    runner.run(iterable, total=total)


async def aio_map(
    func: Callable[[Any], Any],
    iterable: Union[Iterable[Any], AsyncIterable[Any]],
    n_workers: int = 10,
    cache_path: Optional[str] = None,
    key_field: str = "id",
    save_frequency: int = 1000,
    total: Optional[int] = None
):
    """
    Async map using asyncio.
    """
    store = None
    if cache_path:
        store = JsonlStore(path=cache_path, key_field=key_field, flush_interval=save_frequency)

    runner = AsyncRunner(
        func=func, 
        n_workers=n_workers, 
        store=store
    )
    await runner.run(iterable, total=total)
