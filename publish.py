import time
import json
from redis_json import Redis


redis = Redis()


def pub(count):
    for i in range(0, count):
        data = {"Key": f"Value_{str(i)}"}
        redis.setData(key="deneme-datası", value=data)
        redis.publish(channel="deneme", message=json.dumps(data))
        time.sleep(5)


if __name__ == "__main__":
    pub(100)
