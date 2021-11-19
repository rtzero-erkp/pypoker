import collections
from typing import List, Dict, Optional

from .card import Card


class Cards:
    def __init__(self, cards: List[Card], lowest_rank=2):
        # Sort the list of cards in a descending order
        self._sorted = sorted(cards, key=int, reverse=True)
        self._lowest_rank: int = lowest_rank

    def _group_by_ranks(self) -> Dict[int, List[Card]]:
        # Group cards by their ranks.
        # Returns a dictionary keyed by rank and valued by list of cards with the same rank.
        # Each list is sorted by card values in a descending order.
        ranks = collections.defaultdict(list)
        for card in self._sorted:
            ranks[card.rank].append(card)
        return ranks

    def _x_sorted_list(self, x) -> List[List[Card]]:
        """
        If x = 2 returns a list of pairs, if 3 a list of trips, ...
        The list is sorted by sublist ranks.
        If x = 2 and there is a pair of J and a pair of K, the pair of K will be the first element of the list.
        Every sublist is sorted by card suit.
        If x = 4 and the there is a quads of A's, then the quad will be sorted: A of hearts, A of diamonds, ...
        :param x: dimension of every sublist
        :return: a list of a list of cards
        """
        return sorted(
            (cards for cards in self._group_by_ranks().values() if len(cards) == x),
            key=lambda cards: cards[0].rank,
            reverse=True
        )

    def _get_straight(self, sorted_cards):
        if len(sorted_cards) < 5:
            return None

        straight = [sorted_cards[0]]

        for i in range(1, len(sorted_cards)):
            if sorted_cards[i].rank == sorted_cards[i - 1].rank - 1:
                straight.append(sorted_cards[i])
                if len(straight) == 5:
                    return straight
            elif sorted_cards[i].rank != sorted_cards[i - 1].rank:
                straight = [sorted_cards[i]]

        # The Ace can go under the lowest rank card
        if len(straight) == 4 and sorted_cards[0].rank == 14 and straight[-1].rank == self._lowest_rank:
            straight.append(sorted_cards[0])
            return straight
        return None

    def _merge_with_cards(self, score_cards: List[Card]):
        return score_cards + [card for card in self._sorted if card not in score_cards]

    def quads(self):
        quads_list = self._x_sorted_list(4)
        try:
            return self._merge_with_cards(quads_list[0])[0:5]
        except IndexError:
            return None

    def full_house(self) -> Optional[List[Card]]:
        trips_list = self._x_sorted_list(3)
        pair_list = self._x_sorted_list(2)
        try:
            return self._merge_with_cards(trips_list[0] + pair_list[0])[0:5]
        except IndexError:
            return None

    def trips(self) -> Optional[List[Card]]:
        trips_list = self._x_sorted_list(3)
        try:
            return self._merge_with_cards(trips_list[0])[0:5]
        except IndexError:
            return None

    def two_pair(self) -> Optional[List[Card]]:
        pair_list = self._x_sorted_list(2)
        try:
            return self._merge_with_cards(pair_list[0] + pair_list[1])[0:5]
        except IndexError:
            return None

    def pair(self) -> Optional[List[Card]]:
        pair_list = self._x_sorted_list(2)
        try:
            return self._merge_with_cards(pair_list[0])[0:5]
        except IndexError:
            return None

    def straight(self) -> Optional[List[Card]]:
        return self._get_straight(self._sorted)

    def flush(self) -> Optional[List[Card]]:
        suits = collections.defaultdict(list)
        for card in self._sorted:
            suits[card.suit].append(card)
            # Since cards is sorted, the first flush detected is guaranteed to be the highest one
            if len(suits[card.suit]) == 5:
                return suits[card.suit]
        return None

    def straight_flush(self) -> Optional[List[Card]]:
        suits = collections.defaultdict(list)
        for card in self._sorted:
            suits[card.suit].append(card)
            if len(suits[card.suit]) >= 5:
                straight = self._get_straight(suits[card.suit])
                # Since cards is sorted, the first straight flush detected is guaranteed to be the highest one
                if straight:
                    return straight
        return None

    def no_pair(self) -> List[Card]:
        return self._sorted[0:5]


class Score:
    def __init__(self, category: int, cards: List[Card]):
        self._category: int = category
        self._cards: List[Card] = cards
        assert (len(cards) <= 5)

    @property
    def category(self) -> int:
        """Gets the category for this score."""
        return self._category

    @property
    def cards(self) -> List[Card]:
        return self._cards

    @property
    def strength(self) -> int:
        raise NotImplemented

    def cmp(self, other):
        raise NotImplemented

    def dto(self):
        return {
            "category": self.category,
            "cards": [card.dto() for card in self.cards]
        }


class ShortPokerScore(Score):
    NO_PAIR = 0
    PAIR = 1
    TWO_PAIR = 2
    TRIPS = 3
    STRAIGHT = 4
    FULL_HOUSE = 5
    FLUSH = 6
    QUADS = 7
    STRAIGHT_FLUSH = 8

    @property
    def strength(self) -> int:
        strength = self.category
        for offset in range(5):
            strength <<= 4
            try:
                strength += self.cards[offset].rank
            except IndexError:
                pass
        for offset in range(5):
            strength <<= 2
            try:
                strength += self.cards[offset].suit
            except IndexError:
                pass
        return strength

    def cmp(self, other):
        # Same score, compare the list of cards
        cards1 = self.cards
        cards2 = other.cards

        # In a traditional poker, royal flushes are weaker than minimum straight flushes
        # This is done so you are not mathematically sure to have the strongest hand.
        if self.category == ShortPokerScore.STRAIGHT_FLUSH:
            if ShortPokerScore._straight_is_max(cards1) and ShortPokerScore._straight_is_min(cards2):
                return -1
            elif ShortPokerScore._straight_is_min(cards1) and ShortPokerScore._straight_is_max(cards2):
                return 1

        if self.strength < other.strength:
            return -1
        elif self.strength > other.strength:
            return 1
        else:
            return 0

    @staticmethod
    def _straight_is_min(straight_sequence) -> bool:
        return straight_sequence[4].rank == 14

    @staticmethod
    def _straight_is_max(straight_sequence) -> bool:
        return straight_sequence[0].rank == 14


class LongPokerScore(Score):
    NO_PAIR = 0
    PAIR = 1
    TWO_PAIR = 2
    TRIPS = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    QUADS = 7
    STRAIGHT_FLUSH = 8

    @property
    def strength(self):
        strength = self.category
        for offset in range(5):
            strength <<= 4
            try:
                strength += self.cards[offset].rank
            except IndexError:
                pass
        return strength

    def cmp(self, other):
        if self.strength < other.strength:
            return -1
        elif self.strength > other.strength:
            return 1
        else:
            return 0


class ScoreDetector:
    def get_score(self, cards: List[Card]):
        raise NotImplemented


class ShortPokerScoreDetector(ScoreDetector):
    def __init__(self, lowest_rank):
        self._lowest_rank = lowest_rank

    def get_score(self, cards):
        cards = Cards(cards, self._lowest_rank)

        score_functions = [
            (ShortPokerScore.STRAIGHT_FLUSH, cards.straight_flush),
            (ShortPokerScore.QUADS, cards.quads),
            (ShortPokerScore.FLUSH, cards.flush),
            (ShortPokerScore.FULL_HOUSE, cards.full_house),
            (ShortPokerScore.STRAIGHT, cards.straight),
            (ShortPokerScore.TRIPS, cards.trips),
            (ShortPokerScore.TWO_PAIR, cards.two_pair),
            (ShortPokerScore.PAIR, cards.pair),
            (ShortPokerScore.NO_PAIR, cards.no_pair),
        ]

        for score_category, score_function in score_functions:
            score = score_function()
            if score:
                return ShortPokerScore(score_category, score)

        raise RuntimeError("Unable to detect the score")


class LongPokerScoreDetector(ScoreDetector):
    def get_score(self, cards):
        cards = Cards(cards, 2)
        score_functions = [
            (LongPokerScore.STRAIGHT_FLUSH, cards.straight_flush),
            (LongPokerScore.QUADS, cards.quads),
            (LongPokerScore.FULL_HOUSE, cards.full_house),
            (LongPokerScore.FLUSH, cards.flush),
            (LongPokerScore.STRAIGHT, cards.straight),
            (LongPokerScore.TRIPS, cards.trips),
            (LongPokerScore.TWO_PAIR, cards.two_pair),
            (LongPokerScore.PAIR, cards.pair),
            (LongPokerScore.NO_PAIR, cards.no_pair),
        ]

        for score_category, score_function in score_functions:
            cards = score_function()
            if cards:
                return LongPokerScore(score_category, cards)

        raise RuntimeError("Unable to detect the score")


class CustomPokerScoreDetector(ScoreDetector):
    def __init__(self, lowest_rank):
        self._lowest_rank = lowest_rank

    def get_score(self, cards):
        cards = Cards(cards, self._lowest_rank)

        score_functions = [  # 比牌规则
            (LongPokerScore.STRAIGHT_FLUSH, cards.straight_flush),  # 同花顺
            (LongPokerScore.QUADS, cards.quads),  # 四条
            (LongPokerScore.FLUSH, cards.flush),  # 同花
            (LongPokerScore.FULL_HOUSE, cards.full_house),  # 葫芦
            (LongPokerScore.STRAIGHT, cards.straight),  # 顺子
            (LongPokerScore.TRIPS, cards.trips),  # 三条
            (LongPokerScore.TWO_PAIR, cards.two_pair),  # 两对
            (LongPokerScore.PAIR, cards.pair),  # 一对
            (LongPokerScore.NO_PAIR, cards.no_pair),  # 高牌
        ]

        for score_category, score_function in score_functions:
            score = score_function()
            if score:
                return ShortPokerScore(score_category, score)

        raise RuntimeError("Unable to detect the score")
