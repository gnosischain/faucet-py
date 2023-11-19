from datetime import datetime, timedelta
from cachetools import TTLCache


class Cache:
    def __init__(self, limit_seconds):
        self.cache = TTLCache(maxsize=10, ttl=timedelta(seconds=limit_seconds), timer=datetime.now)

    def limit_by_address(self, address):
        cached = self.cache.get(address, False)
        if not cached:
            self.cache[address] = datetime.now()
        return cached
    
    def delete(self, attr):
       self.cache.pop(attr)

    def clear(self):
        self.cache.clear()