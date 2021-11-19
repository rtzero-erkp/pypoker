import logging
import redis
import os

from poker.game_server_redis import GameServerRedis
from poker.game_room import GameRoomFactory
from poker.poker_game_custom import CustomPokerGameFactory

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if 'DEBUG' in os.environ else logging.INFO)
    logger = logging.getLogger()

    redis_url = "redis://192.168.199.220:6379"

    server = GameServerRedis(
        redis=redis.from_url(redis_url),
        connection_channel="custom-poker:lobby",
        room_factory=GameRoomFactory(
            room_size=10,
            game_factory=CustomPokerGameFactory(
                big_blind=40.0,
                small_blind=20.0,
                logger=logger,
                game_subscribers=[]
            )
        ),
        logger=logger
    )
    server.start()
