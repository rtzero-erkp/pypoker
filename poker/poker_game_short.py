import uuid
from typing import List, Optional

from .deck import DeckFactory
from .player import Player
from .poker_game import GameFactory, GamePlayers, GameSubscriber
from .poker_game_holdem import HoldemPokerGameEventDispatcher, HoldemPokerGame
from .score_detector import ShortPokerScoreDetector


class ShortPokerGameFactory(GameFactory):
    def __init__(self, big_blind: float, small_blind: float, logger, game_subscribers: Optional[List[GameSubscriber]] = None):
        self._big_blind: float = big_blind
        self._small_blind: float = small_blind
        self._logger = logger
        self._game_subscribers: List[GameSubscriber] = [] if game_subscribers is None else game_subscribers

    def create_game(self, players: List[Player]):
        lowest_rank = 6  # 短牌从牌6开始
        game_id = str(uuid.uuid4())

        event_dispatcher = HoldemPokerGameEventDispatcher(game_id=game_id, logger=self._logger)
        for subscriber in self._game_subscribers:
            event_dispatcher.subscribe(subscriber)

        return HoldemPokerGame(
            self._big_blind,
            self._small_blind,
            id=game_id,
            game_players=GamePlayers(players),
            event_dispatcher=event_dispatcher,
            deck_factory=DeckFactory(lowest_rank),
            score_detector=ShortPokerScoreDetector(lowest_rank)
        )
