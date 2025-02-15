import time
from typing import Generator

from redis import Redis

from . import define
from .game_room import GameRoomFactory
from .channel_redis import MessageQueue, ChannelRedis, ChannelError, MessageFormatError, MessageTimeout
from .game_server import GameServer, ConnectedPlayer
from .player_server import PlayerServer
from .utils import *


class GameServerRedis(GameServer):
    def __init__(self, redis: Redis, connection_channel: str, room_factory: GameRoomFactory, logger=None):
        GameServer.__init__(self, room_factory, logger)
        self._redis: Redis = redis
        self._connection_queue = MessageQueue(redis, connection_channel)

    def _connect_player(self, message) -> ConnectedPlayer:
        self.show()
        if define.SHOW_LOG:
            info(f"message:{message}")

        try:
            timeout_epoch = int(message["timeout_epoch"])
        except KeyError:
            raise MessageFormatError(attribute="timeout_epoch", desc="Missing attribute")
        except ValueError:
            raise MessageFormatError(attribute="timeout_epoch", desc="Invalid session id")

        if timeout_epoch < time.time():
            raise MessageTimeout("Connection timeout")

        try:
            session_id = str(message["session_id"])
        except KeyError:
            raise MessageFormatError(attribute="session", desc="Missing attribute")
        except ValueError:
            raise MessageFormatError(attribute="session", desc="Invalid session id")

        try:
            player_id = str(message["player"]["id"])
        except KeyError:
            raise MessageFormatError(attribute="player.id", desc="Missing attribute")
        except ValueError:
            raise MessageFormatError(attribute="player.id", desc="Invalid player id")

        try:
            player_name = str(message["player"]["name"])
        except KeyError:
            raise MessageFormatError(attribute="player.name", desc="Missing attribute")
        except ValueError:
            raise MessageFormatError(attribute="player.name", desc="Invalid player name")

        try:
            player_money = float(message["player"]["money"])
        except KeyError:
            raise MessageFormatError(attribute="player.money", desc="Missing attribute")
        except ValueError:
            raise MessageFormatError(attribute="player.money",
                                     desc="'{}' is not a number".format(message["player"]["money"]))

        try:
            game_room_id = str(message["room_id"])
        except KeyError:
            game_room_id = None
        except ValueError:
            raise MessageFormatError(attribute="room_id", desc="Invalid room id")

        player = PlayerServer(
            channel=ChannelRedis(
                self._redis,
                "poker5:player-{}:session-{}:I".format(player_id, session_id),
                "poker5:player-{}:session-{}:O".format(player_id, session_id)
            ),
            logger=self._logger,
            id=player_id,
            name=player_name,
            money=player_money,
        )

        # Acknowledging the connection

        player.send_message({
            "message_type": "connect",
            "server_id": self._id,
            "player": player.dto()
        })

        self.show()
        return ConnectedPlayer(player=player, room_id=game_room_id)

    def new_players(self) -> Generator[ConnectedPlayer, None, None]:

        self.show()
        while True:
            try:
                yield self._connect_player(self._connection_queue.pop())
            except (ChannelError, MessageTimeout, MessageFormatError) as e:
                self._logger.error("Unable to connect the player: {}".format(e.args[0]))
