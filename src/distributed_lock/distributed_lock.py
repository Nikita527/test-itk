import datetime
import functools

import redis

redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"single_lock:{func.__module__}.{func.__name__}"
            lock_ttl = int(max_processing_time.total_seconds())
            acquired = redis_client.set(
                lock_key, "locked", nx=True, ex=lock_ttl
            )
            if not acquired:
                raise RuntimeError(
                    f"Function {func.__name__} is already running elsewhere"
                )
            try:
                return func(*args, **kwargs)
            finally:
                redis_client.delete(lock_key)

        return wrapper

    return decorator
