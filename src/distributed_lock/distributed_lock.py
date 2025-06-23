import datetime
import functools
import uuid

import redis

redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)

RELEASE_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"single_lock:{func.__module__}.{func.__name__}"
            lock_ttl = int(max_processing_time.total_seconds())
            token = str(uuid.uuid4())
            acquired = redis_client.set(
                lock_key, token, nx=True, ex=lock_ttl
            )
            if not acquired:
                raise RuntimeError(
                    f"Function {func.__name__} is already running elsewhere"
                )
            try:
                return func(*args, **kwargs)
            finally:
                redis_client.eval(RELEASE_LUA, 1, lock_key, token)

        return wrapper

    return decorator
