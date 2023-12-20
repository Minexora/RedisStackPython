import time
import json
from redis_json import Redis

redis = Redis()


def sub_func(data):
    print(json.loads(data))


def sub():
    redis.subscribe(channel="deneme", func=sub_func)


if __name__ == "__main__":
    sub()
    while True:
        time.sleep(1)
