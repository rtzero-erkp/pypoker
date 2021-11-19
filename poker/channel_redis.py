import json
import signal
import time
from typing import Optional, Any

import gevent
from redis import exceptions, Redis

from . import define
from .channel import Channel, MessageFormatError, MessageTimeout, ChannelError
from .utils import *


class RedisListener:
    def __init__(self, redis: Redis, channel: str):
        self._pubsub = redis.pubsub()
        self._pubsub.subscribe(channel)

    def close(self):
        self._pubsub.unsubscribe()

    def recv_message(self, timeout_epoch: Optional[float] = None):
        def timeout_handler(signum, frame):
            raise MessageTimeout("Timed out")

        if timeout_epoch:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(round(timeout_epoch - time.time())))

        try:
            for message in self._pubsub.listen():
                if message["type"] == "message":
                    return json.loads(message["data"])
        except ValueError:
            # Invalid json
            raise MessageFormatError(desc="Unable to decode the JSON message")
        finally:
            if timeout_epoch:
                signal.alarm(0)


class RedisPublisher:
    def __init__(self, redis: Redis, channel: str):
        self._redis = redis
        self._channel = channel

    def send_message(self, message):
        # Encode the message
        msg_serialized = json.dumps(message)
        msg_encoded = msg_serialized.encode("utf-8")
        self._redis.publish(self._channel, msg_encoded)


class RedisPubSub(Channel):
    def __init__(self, redis: Redis, channel_in: str, channel_out: str):
        self._listener = RedisListener(redis, channel_in)
        self._publisher = RedisPublisher(redis, channel_out)

    def close(self):
        self._listener.close()

    def recv_message(self, timeout_epoch: Optional[float] = None):
        return self._listener.recv_message(timeout_epoch)

    def send_message(self, message):
        self._publisher.send_message(message)


class MessageQueue:
    def __init__(self, redis: Redis, queue_name: str, expire: int = 300):
        self._redis: Redis = redis
        self._queue_name: str = queue_name
        self._expire: int = expire

    @property
    def name(self):
        return self._queue_name

    def push(self, message: Any):
        if define.SHOW_LOG:
            info(f"[redis:push] {message}")
        msg_serialized = json.dumps(message)
        msg_encoded = msg_serialized.encode("utf-8")
        try:
            self._redis.lpush(self._queue_name, msg_encoded)
            self._redis.expire(self._queue_name, self._expire)
        except exceptions.RedisError as e:
            raise ChannelError(e.args[0])

    def pop(self, timeout_epoch: Optional[float] = None) -> Any:
        while timeout_epoch is None or time.time() < timeout_epoch:
            try:
                response = self._redis.rpop(self._queue_name)
                if response is not None:
                    try:
                        # Deserialize and return the message
                        message = json.loads(response)
                        if define.SHOW_LOG:
                            info(f"[redis:pop] {message}")
                        return message
                    except ValueError:
                        # Invalid json
                        raise MessageFormatError(
                            desc="Unable to decode the JSON message")
                else:
                    # Context switching
                    gevent.sleep(0.01)
            except exceptions.RedisError as ex:
                raise ChannelError(ex.args[0])
        raise MessageTimeout("Timed out")


class ChannelRedis(Channel):
    def __init__(self, redis: Redis, channel_in: str, channel_out: str):
        if define.SHOW_LOG:
            info(f"[redis:init]")
        self._queue_in = MessageQueue(redis, channel_in)
        self._queue_out = MessageQueue(redis, channel_out)

    def send_message(self, message: Any):
        if define.SHOW_LOG:
            info(f"[redis:send] {message}")
        self._queue_out.push(message)

    def recv_message(self, timeout_epoch: Optional[float] = None) -> Any:
        message = self._queue_in.pop(timeout_epoch)
        if define.SHOW_LOG:
            info(f"[redis:recv] {message}")
        return message
