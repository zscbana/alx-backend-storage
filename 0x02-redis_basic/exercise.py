#!/usr/bin/env python3
""" 0x02. Redis basic
"""
import redis
import uuid
from typing import Any, Callable, Union


class Cache():
    """ Cache class"""
    def __init__(self) -> None:
        """Init """
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis"""
        DKey = str(uuid.uuid4())
        self._redis.set(DKey, data)
        return DKey

    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """Get data from Redis"""
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """Get string data from Redis"""
        val = self.get(key)
        if val is not None:
            return val.decode('utf-8')
        return ''

    def get_int(self, key: str) -> int:
        """Get integer data from Redis"""
        val = self.get(key)
        if val:
            return int(val)
        return
