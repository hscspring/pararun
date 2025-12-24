import concurrent.futures
from typing import Callable, Iterable, Any, Optional

from tqdm import tqdm

from .store import KVStore


class ExecutorRunner:
    def __init__(
        self, 
        func: Callable[[Any], Any],
        n_workers: int = 4,
        executor_type: str = "process", # "process" or "thread"
        store: Optional[KVStore] = None
    ):
        self.func = func
        self.n_workers = n_workers
        self.executor_type = executor_type
        self.store = store

    def run(self, iterable: Iterable[Any], total: Optional[int] = None):
        processed_keys = set()
        if self.store:
            processed_keys = self.store.load()

        Executor = (
            concurrent.futures.ProcessPoolExecutor 
            if self.executor_type == "process" 
            else concurrent.futures.ThreadPoolExecutor
        )
        
        with Executor(max_workers=self.n_workers) as executor:
            futures = {} # future -> item
            pending_futures = set()
            max_queue_size = self.n_workers * 2

            iterator = iter(iterable)
            
            pbar = tqdm(total=total)

            while True:
                # Fill queue from iterator
                while len(pending_futures) < max_queue_size:
                    try:
                        item = next(iterator)
                        
                        # Idempotency check
                        if self.store:
                            key = self.store.get_key(item)
                            if key in processed_keys:
                                if pbar.total: 
                                    pbar.total = max(0, pbar.total - 1)
                                    pbar.refresh()
                                continue
                        
                        fut = executor.submit(self.func, item)
                        futures[fut] = item
                        pending_futures.add(fut)
                        
                    except StopIteration:
                        break
                
                if not pending_futures:
                    break
                
                # Wait for at least one task to complete
                done, _ = concurrent.futures.wait(
                    pending_futures, 
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                # Process done tasks
                for future in done:
                    pending_futures.remove(future)
                    item = futures.pop(future, None)
                    try:
                        result = future.result()
                        if self.store:
                            self.store.append(result)
                    except Exception as e:
                        print(f"[ERROR] Task failed for {item}: {e}")
                    finally:
                        pbar.update(1)
            
            pbar.close()
            
            if self.store:
                self.store.flush()
