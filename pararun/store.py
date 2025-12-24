import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Set, List


class KVStore(ABC):
    @abstractmethod
    def load(self) -> Set[Any]:
        """Load and return simple set of processed keys."""
        pass

    @abstractmethod
    def append(self, result: Any) -> None:
        """Append a result to the store."""
        pass

    @abstractmethod
    def flush(self) -> None:
        """Flush buffer to storage."""
        pass

    @abstractmethod
    def get_key(self, item: Any) -> Any:
        """Extract key from an item."""
        pass


class JsonlStore(KVStore):
    def __init__(self, path: str, key_field: str = "id", flush_interval: int = 1000):
        self.path = path
        self.key_field = key_field
        self.flush_interval = flush_interval
        self.buffer: List[Dict[str, Any]] = []
        self._processed_keys: Set[Any] = set()
        
        # Load existing keys if file exists
        if os.path.exists(self.path):
            self._load_keys()

    def _load_keys(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if self.key_field in data:
                            self._processed_keys.add(data[self.key_field])
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[WARN] Failed to load existing cache from {self.path}: {e}")

    def load(self) -> Set[Any]:
        return self._processed_keys

    def append(self, result: Dict[str, Any]) -> None:
        if self.key_field in result:
            self._processed_keys.add(result[self.key_field])
        
        self.buffer.append(result)
        if len(self.buffer) >= self.flush_interval:
            self.flush()

    def flush(self) -> None:
        if not self.buffer:
            return
        
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                for item in self.buffer:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            self.buffer.clear()
        except Exception as e:
            print(f"[ERROR] Failed to write cache to {self.path}: {e}")

    def get_key(self, item: Any) -> Any:
        if isinstance(item, dict) and self.key_field in item:
            return item[self.key_field]
        return str(item)
