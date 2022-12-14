import os
import redis
from dotenv import load_dotenv

load_dotenv()


class Redis:
    def __init__(self):
        self.redis = redis.Redis(host=os.getenv('RedisHost'), port=os.getenv('RedisPort'))

    def setData(self, key, value, time=None):
        self.redis.json().set(path="$", name=key, obj=value)
        if time is not None:
            self.redis.expire(key, time)

    def getData(self, key):
        return self.redis.json().get(name=key)

    def deleteData(self, key):
        if self.redis.exists(key):
            self.redis.delete(key)

    def clearData(self):
        self.redis.flushall()


# if __name__ == '__main__':
#     data = {
#         "name": 'deneme',
#         "id": 1,
#         "email": "deneme@gmail.com",
#         "password": "deneme",
#     }
#     rds = Redis()
#     rds.setData('one', data)
#     rds.setData('two', data, os.getenv('RedisCacheTime'))
    # print(rds.getData('one'))
    # rds.deleteData('two')
    # rds.deleteData('to')
    # rds.clearData()
