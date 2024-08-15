#!/usr/bin/env python3
""" 0x02. Redis basic
"""
import redis
import uuid
from typing import Any, Callable, Union
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """ Counts the number of calls to a method"""
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """ Invoker function"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    """ Stores the history of calls to a method"""
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """ Invoker function"""
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    """ Replay the history of a function"""
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


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

    @count_calls
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
