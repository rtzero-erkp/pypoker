import logging
import redis
import os

from poker.game_server_redis import GameServerRedis
from poker.game_room import GameRoomFactory
from poker.poker_game_short import ShortPokerGameFactory

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if 'DEBUG' in os.environ else logging.INFO)
    logger = logging.getLogger()

    redis_url = "redis://192.168.199.220:6379"

    server = GameServerRedis(
        redis=redis.from_url(redis_url),
        connection_channel="short-poker:lobby",
        room_factory=GameRoomFactory(
            room_size=5,
            game_factory=ShortPokerGameFactory(blind=10.0, logger=logger)
        ),
        logger=logger
    )
    server.start()
