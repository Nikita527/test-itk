import random
import time

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(
        self,
        key="rate_limiter",
        window=3,
        limit=5,
        host="127.0.0.1",
        port=6379,
        db=0,
    ):
        self.redis = redis.StrictRedis(host=host, port=port, db=db)
        self.key = key
        self.window = window
        self.limit = limit

    def test(self) -> bool:
        now = time.time()
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(self.key, 0, now - self.window)
        pipe.zadd(self.key, {str(now): now})
        pipe.zcard(self.key)
        pipe.expire(self.key, self.window + 1)
        _, _, count, _ = pipe.execute()
        return count <= self.limit


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(10):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")

    for _ in range(10):

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
