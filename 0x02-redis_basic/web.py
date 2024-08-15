#!/usr/bin/env python3
'''Correction of "5. Implementing an expiring web cache and tracker"
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    '''A decorator that caches the result of a method call in Redis.'''
    @wraps(method)
    def invoker(url) -> str:
        '''Fetches data from the given URL and caches it.'''
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Fetches a page and caches the result.'''
    return requests.get(url).text
