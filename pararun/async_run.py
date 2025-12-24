import asyncio
from typing import Callable, Iterable, Any, Optional, Union, AsyncIterable

from tqdm.asyncio import tqdm

from .store import KVStore


class AsyncRunner:
    def __init__(
        self, 
        func: Callable[[Any], Any],
        n_workers: int = 10,
        store: Optional[KVStore] = None
    ):
        self.func = func
        self.n_workers = n_workers
        self.store = store
        self.queue = asyncio.Queue(maxsize=n_workers * 2)

    async def _worker(self, pbar: Optional[tqdm]):
        while True:
            item = await self.queue.get()
            if item is None:
                self.queue.task_done()
                break
            
            try:
                if asyncio.iscoroutinefunction(self.func):
                    result = await self.func(item)
                else:
                    result = self.func(item)
                
                if self.store:
                    self.store.append(result)
            
            except Exception as e:
                # TODO: proper error handling
                print(f"[ERROR] Task failed: {e}")
            finally:
                self.queue.task_done()
                if pbar:
                    pbar.update(1)

    async def run(
        self, 
        iterable: Union[Iterable[Any], AsyncIterable[Any]], 
        total: Optional[int] = None
    ):
        processed_keys = set()
        if self.store:
            processed_keys = self.store.load()
        
        # Start workers
        pbar = tqdm(total=total) if total else None
        workers = [asyncio.create_task(self._worker(pbar)) for _ in range(self.n_workers)]
        
        # Producer loop
        if isinstance(iterable, AsyncIterable):
             async for item in iterable:
                if self.store:
                    key = self.store.get_key(item)
                    if key in processed_keys:
                        if pbar: pbar.total -= 1
                        continue
                 
                await self.queue.put(item)
        else:
            for item in iterable:
                if self.store:
                    key = self.store.get_key(item)
                    if key in processed_keys:
                        if pbar and pbar.total: 
                            pbar.total = max(0, pbar.total - 1)
                            pbar.refresh()
                        continue
                
                await self.queue.put(item)

        # Stop signal
        for _ in range(self.n_workers):
            await self.queue.put(None)
        
        # Wait
        await self.queue.join()
        for w in workers:
            w.cancel()
        
        if pbar:
            pbar.close()
            
        if self.store:
            self.store.flush()
