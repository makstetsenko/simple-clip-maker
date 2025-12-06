from typing import Callable
import os
import json


class JsonCache:
    def __init__(self):
        self.path = "./cache"
        os.makedirs(self.path, exist_ok=True)

    def get(self, key: str) -> dict | None:
        cache_path = self.get_cache_path(key)

        if os.path.isfile(cache_path):
            with open(cache_path, "r") as f:
                return json.loads(f.read())

        return None

    def set(self, key: str, value: dict):
        cache_path = self.get_cache_path(key)

        with open(cache_path, "w") as f:
            f.write(json.dumps(value, indent=4, sort_keys=False, ensure_ascii=False))

    def get_cache_path(self, key):
        return self.path + "/" + key + ".json"
