import os
import ast
import redis
import logging
import threading
from config.conf import Config
from dotenv import load_dotenv
from redis.sentinel import Sentinel

load_dotenv()

conf_cls = Config()
config = conf_cls()


class Redis:
    use_redis_type = None
    sentinel = None
    redis_host = None
    redis_port = None
    connection_timeout_ms = None
    master_alias = None
    password = None

    def get_conf(self):
        import json
        print(json.dumps({"use_redis_type": self.use_redis_type, "redis_host": self.redis_host, "redis_port": self.redis_port, "connection_timeout_ms": self.connection_timeout_ms, "sentinel": self.sentinel, "master_alias": self.master_alias, "password": self.password}, indent=4))

    def __init__(self):
        try:
            use_redis_type = self.check_redis_type()
            self.use_redis_type = use_redis_type
            if use_redis_type is None or use_redis_type == "default":
                redis_host = os.getenv("RedisHost", None)
                self.redis_host = redis_host
                redis_port = os.getenv("RedisPort", None)
                self.redis_port = redis_port
                connection_timeout_ms = os.getenv("RedisConnectionTimeoutMs", 15000)
                self.connection_timeout_ms = connection_timeout_ms
                if redis_host and redis_port:
                    self.redis = redis.Redis(host=redis_host, port=redis_port, socket_timeout=int(connection_timeout_ms))
                    if self.redis.ping():
                        print("Redis is up and running")
                    else:
                        print("Master is not available")
                    logging.info("Redis connection completed successfully.")
                else:
                    logging.error("Failed to connect to Redis. Host and Port information not found!")
            elif use_redis_type == "sentinel":
                sentinel = os.getenv("REDIS_SENTINEL", None)
                self.sentinel = ast.literal_eval(sentinel)
                master_alias = os.getenv("REDIS_MASTER_ALIAS", None)
                self.master_alias = master_alias
                password = os.getenv("REDIS_PASSWORD", None)
                self.password = password
                connection_timeout_ms = os.getenv("RedisConnectionTimeoutMs", 15000)
                self.connection_timeout_ms = connection_timeout_ms
                redis_sentinel = Sentinel(ast.literal_eval(sentinel), password=password, socket_timeout=int(connection_timeout_ms))
                self.redis = redis_sentinel.master_for(master_alias, socket_timeout=int(connection_timeout_ms))
                if self.redis.ping():
                    print("Redis is up and running")
                else:
                    print("Master is not available")
                logging.info("Redis connection completed successfully.")
            else:
                logging.error("Could not connect to Redis. The property named 'use_redis_type' is not correctly specified in the 'redis_config' object in the configuration file.")
        except Exception as e:
            logging.error("Failed to connect to Redis. Error Occurred: {}".format(str(e)))

    def check_redis_type(self):
        use_redis_type = config.get("file_config", {}).get("redis_config", {}).get("use_redis_type", None)
        if use_redis_type:
            return use_redis_type
        else:
            logging.error("Could not connect to Redis. You must specify the property named 'use_redis_type' in the 'redis_config' object in the config file. Default value is set to 'default'.")
            return None

    def get_prefix_name(self, key):
        prefix = os.getenv("REDIS_PREFIX", None)
        if prefix:
            return f"{prefix}_{key}"
        else:
            return key

    def setData(self, key, value, time=None):
        try:
            self.redis.json().set(path="$", name=self.get_prefix_name(key=key), obj=value)
            if time is not None:
                self.redis.expire(key, time)
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))

    def setTime(self, key, time):
        try:
            self.redis.expire(self.get_prefix_name(key=key), time)
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))

    def exists(self, key):
        try:
            return self.redis.exists(self.get_prefix_name(key=key))
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))
            return False

    def getData(self, key):
        try:
            return self.redis.json().get(name=self.get_prefix_name(key=key))
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))

    def getKeyTtl(self, key):
        try:
            return self.redis.ttl(self.get_prefix_name(key=key))
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))

    def append_data(self, key, appended_data):
        redis_data = None
        try:
            if self.exists(self.get_prefix_name(key=key)):
                redis_data = self.getData(self.get_prefix_name(key=key))
                redis_data = {**redis_data, **appended_data}
                self.setData(self.get_prefix_name(key=key), redis_data)
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))
        return redis_data

    def delete_data(self, redis_key, delete_keys=None):
        redis_data = None
        try:
            if self.exists(self.get_prefix_name(key=redis_key)):
                redis_data = self.getData(redis_key)
                if type(delete_keys) == str:
                    delete_keys = [delete_keys]
                for key in delete_keys:
                    if key in redis_data:
                        del redis_data[key]
                self.setData(self.get_prefix_name(key=redis_key), redis_data)
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))
        return redis_data

    def deleteData(self, key):
        try:
            self.redis.delete(self.get_prefix_name(key=key))
        except Exception as e:
            logging.error("Redis --> Error Occurred: {}".format(str(e)))

    def clearData(self):
        try:
            self.redis.flushall()
        except Exception as e:
            logging.error("Redis --> Redis --> Error Occurred: {}".format(str(e)))

    def publish(self, channel, message, **kwargs):
        try:
            self.redis.publish(channel=channel, message=message, kwargs=kwargs)
        except Exception as e:
            logging.error(str(e))

    def subscribe(self, channel, func):
        def pub_sub_func(channel, func):
            try:
                pubsub = self.redis.pubsub()
                pubsub.subscribe(channel)
                while True:
                    for m in pubsub.listen():
                        logging.info("Gelen mesaj: ")
                        logging.info(m)
                        data = m.get("data", {})
                        if type(data) != int and data != {}:
                            func(data)
            except Exception as e:
                logging.error(str(e))

        t = threading.Thread(target=pub_sub_func, args=[channel, func])
        t.setDaemon(True)
        t.start()
