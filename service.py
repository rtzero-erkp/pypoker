import logging
import redis
import os

from poker import define
from poker.game_server_redis import GameServerRedis
from poker.game_room import GameRoomFactory
from poker.poker_game_custom import CustomPokerGameFactory
from poker.poker_game_long import LongPokerGameFactory
from poker.poker_game_short import ShortPokerGameFactory
from poker.utils import error

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if 'DEBUG' in os.environ else logging.INFO)
    logger = logging.getLogger()

    redis_url = "redis://192.168.199.220:6379"
    game_factory = None
    if define.MODE == define.MODE_CUSTOM:
        game_factory = CustomPokerGameFactory(2 * define.STACK_MULTI, 1 * define.STACK_MULTI, logger, [])
    elif define.MODE == define.MODE_SHORT:
        game_factory = ShortPokerGameFactory(1 * define.STACK_MULTI, logger)
    elif define.MODE == define.MODE_LONG:
        game_factory = LongPokerGameFactory(2 * define.STACK_MULTI, 1 * define.STACK_MULTI, logger, [])
    else:
        error(f"unknown mode:{define.MODE}")
        exit(-1)
    server = GameServerRedis(redis.from_url(redis_url), define.MODE, GameRoomFactory(10, game_factory), logger)
    server.start()
