import os
import ast
import redis
import logging
from config.conf import Config
from redis.sentinel import Sentinel

conf_cls = Config()
config = conf_cls()


class Redis:
    def __init__(self):
        try:
            use_redis_type = self.check_redis_type()
            if use_redis_type is None or use_redis_type == 'default':
                redis_host = config.get('env_config', {}).get('RedisHost', None)
                redis_port = config.get('env_config', {}).get('RedisPort', None)
                if redis_host and redis_port:
                    self.redis = redis.Redis(host=redis_host, port=redis_port)
                    if self.redis.ping():
                        print("Redis is up and running")
                    else:
                        print("Master is not available")
                    logging.info("Redis connection completed successfully.")
                else:
                    logging.error("Failed to connect to Redis. Host and Port information not found!")
            elif use_redis_type == 'sentinel':
                sentinel = config.get('env_config', {}).get('REDIS_SENTINEL', None)
                master_alias = config.get('env_config', {}).get('REDIS_MASTER_ALIAS', None)
                password = config.get('env_config', {}).get('REDIS_PASSWORD', None)
                redis_sentinel = Sentinel(ast.literal_eval(sentinel), password=password, socket_timeout=0.1)
                self.redis = redis_sentinel.master_for(master_alias, socket_timeout=0.1)
                if self.redis.ping():
                    print("Redis is up and running")
                else:
                    print("Master is not available")
                logging.info("Redis connection completed successfully.")
            else:
                logging.error("Could not connect to Redis. The property named 'use_redis_type' is not correctly specified in the 'redis_config' object in the configuration file.")
        except Exception as e:
            logging.error('Failed to connect to Redis. Error Occurred: {}'.format(str(e)))

    def check_redis_type(self):
        use_redis_type = config.get('file_config', {}).get('redis_config', {}).get('use_redis_type', None)
        if use_redis_type:
            return use_redis_type
        else:
            logging.error("Could not connect to Redis. You must specify the property named 'use_redis_type' in the 'redis_config' object in the config file. Default value is set to 'default'.")
            return None

    def setData(self, key, value, time=None):
        try:
            self.redis.json().set(path="$", name=key, obj=value)
            if time is not None:
                self.redis.expire(key, time)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))

    def setTime(self, key, time):
        try:
            self.redis.expire(key, time)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))

    def exists(self, key):
        try:
            return self.redis.exists(key)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))
            return False

    def getData(self, key):
        try:
            return self.redis.json().get(name=key)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))

    def getKeyTtl(self, key):
        try:
            return self.redis.ttl(key)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))

    def append_data(self, key, appended_data):
        redis_data = None
        try:
            if self.exists(key):
                redis_data = self.getData(key)
                redis_data = {**redis_data, **appended_data}
                self.setData(key, redis_data)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))
        return redis_data

    def delete_data(self, redis_key, delete_keys=None):
        redis_data = None
        try:
            if self.exists(redis_key):
                redis_data = self.getData(redis_key)
                if type(delete_keys) == str:
                    delete_keys = [delete_keys]
                for key in delete_keys:
                    if key in redis_data:
                        del redis_data[key]
                self.setData(redis_key, redis_data)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))
        return redis_data

    def deleteData(self, key):
        try:
            self.redis.delete(key)
        except Exception as e:
            logging.error('Redis --> Error Occurred: {}'.format(str(e)))

    def clearData(self):
        try:
            self.redis.flushall()
        except Exception as e:
            logging.error('Redis --> Redis --> Error Occurred: {}'.format(str(e)))
