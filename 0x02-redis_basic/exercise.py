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
