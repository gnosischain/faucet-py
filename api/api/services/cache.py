from datetime import datetime, timedelta

from cachetools import TTLCache


class Cache:
    def __init__(self, limit_seconds):
        self._ttl = limit_seconds
        self.cache = TTLCache(maxsize=10, ttl=timedelta(seconds=limit_seconds), timer=datetime.now)

    def limit_by_address(self, address):
        cached = self.cache.get(address, False)
        if not cached:
            self.cache[address] = datetime.now()
        return cached

    def limit_by_ip(self, ip):
        cached = self.cache.get(ip, False)
        if not cached:
            self.cache[ip] = datetime.now()
        return cached

    def delete(self, attr):
        self.cache.pop(attr)

    def clear(self):
        self.cache.clear()

    def ttl(self, hours=False):
        if hours:
            # 3600 seconds = 1h
            return self._ttl // 3600
        return self._ttl