import redis
import json


class RedisQueue:
    def __init__(self, name="queue", host="127.0.0.1", port=6379, db=0):
        self._redis = redis.StrictRedis(
            host=host, port=port, db=db, decode_responses=True
        )
        self._key = name

    def publish(self, msg: dict):
        self._redis.rpush(self._key, json.dumps(msg))

    def consume(self) -> dict:
        data = self._redis.lpop(self._key)
        if data is not None:
            return json.loads(data)
        return None


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})
    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
