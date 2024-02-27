from datetime import datetime

from api.services import Cache


def test_cache():
    address = '0x' + '0' * 40
    limit_seconds = 1
    cache = Cache(limit_seconds)
    cache.clear()
    cached = cache.limit_by_address(address)
    assert cached == False

    cached = cache.limit_by_address(address)
    assert isinstance(cached, datetime)
