import json
import uuid
from typing import List
from websocket import create_connection
from poker.utils import *

ws_url = "ws://192.168.199.220:5000/poker/lobby"
index_url = "http://192.168.199.220:5000/"
join_url = "http://192.168.199.220:5000/join"


class WSClient:
    def __init__(self, url: str):
        self.conn = create_connection(url)

    def auth(self, pid, name="ws_agent", money=1000, room_id=1):
        session = {
            "player-id": pid,
            "player-name": name,
            "player-money": money,
            "room-id": room_id,
        }
        self.send(session)

    def close(self):
        if self.conn.connected:
            self.conn.close()
        else:
            error("conn closed")

    def alive(self):
        return self.conn.connected

    def send(self, msg: dict):
        if self.conn.connected:
            msg = json.dumps(msg)
            self.conn.send(msg)
        else:
            error("conn closed")

    def recv(self) -> dict:
        if self.conn.connected:
            msg = self.conn.recv()
            dc = json.loads(msg)
            return dc
        else:
            error("conn closed")


class Agent:
    ws: WSClient
    alive: bool
    session: dict
    hand: List
    board: List

    def __init__(self):
        self.pid = str(uuid.uuid4())
        self.name = f"ws_agent"
        self.money = 1000
        self.room_id = 1

    @head_tail
    def connect(self, url: str):
        self.ws = WSClient(url)
        self.ws.auth(self.pid, self.name, self.money, self.room_id)
        self.alive = True
        self.dispatcher()

    @head_tail
    def disconnect(self):
        debug("disconnect", 2)
        self.alive = False
        self.ws.close()

    @head_tail
    def dispatcher(self):
        while self.ws.alive():
            msg = self.ws.recv()
            message_type = msg["message_type"]
            try:
                if message_type == "error":
                    error(f"[recv] type:{message_type}, info:{msg['error']}")
                    self.disconnect()
                elif message_type == "connect":
                    # info(f"[recv] type:{message_type}")
                    pass
                elif message_type == "ping":
                    # info(f"[recv] type:{message_type}")
                    self.ws.send({'message_type': 'pong'})
                elif message_type == "disconnect":
                    error(f"[recv] type:{message_type}")
                    self.disconnect()
                elif message_type == "room-update":
                    event = msg["event"]
                    # info(f"[recv] type:{message_type}, event:{event}, info:{msg}")
                    self.dealt_room_update(msg, event)
                elif message_type == "game-update":
                    # event = msg["event"]
                    # info(f"[recv] type:{message_type}, event:{event}, info:{msg}")
                    self.dealt_game_update(msg)
                else:
                    debug(f"unknown msg.type:{msg['message_type']}")
            except Exception as e:
                error(msg)
                error(e)
                break

    def dealt_room_update(self, msg: json, event: str):
        if event == "init":
            debug(f"msg:{msg}")
        elif event == "player-added":
            _ = {"message_type": "room-update",  # 第一个玩家进入房间
                 "event": "player-added",
                 "room_id": "1",
                 "players": {
                     "ba05d6ac-e42b-4105-b3d5-4e26371dd078": {"id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078", "name": "ws_agent", "money": 1000.0}},
                 "player_ids": ["ba05d6ac-e42b-4105-b3d5-4e26371dd078", "null", "null", "null", "null", "null", "null", "null", "null", "null"],
                 "player_id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078"}
            _ = {"message_type": "room-update",  # 第二个玩家进入房间
                 "event": "player-added",
                 "room_id": "1",
                 "players": {
                     "ba05d6ac-e42b-4105-b3d5-4e26371dd078": {"id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078", "name": "ws_agent", "money": 1000.0},
                     "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47": {"id": "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47", "name": "1", "money": 1000.0}},
                 "player_ids": ["ba05d6ac-e42b-4105-b3d5-4e26371dd078", "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47", "null", "null", "null", "null", "null", "null", "null", "null"],
                 "player_id": "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47"}
            pid = msg["player_id"]
            name = msg["players"][pid]["name"]
            is_self = pid == self.pid
            debug(f"[join] pid:{pid}, name:{name}, is_self:{is_self}")
        elif event == "player-removed":
            _ = {'message_type': 'room-update',
                 'event': 'player-removed', 'room_id': '1',
                 'players': {
                     'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf': {'id': 'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf', 'name': 'ws_agent', 'money': 960.0}},
                 'player_ids': [None, 'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf', None, None, None, None, None, None, None, None],
                 'player_id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47'}
            pid = msg["player_id"]
            # is_self = pid == self.pid
            debug(f"[leave] pid:{pid}")
        else:
            debug(f"unknown event.type:{event}")

    def dealt_game_update(self, msg: json):
        event = msg["event"]
        # game_type = msg["game_type"]
        if event == "new-game":
            _ = {"message_type": "game-update",
                 "game_id": "35fc022f-468c-4e93-a069-a9da0e52526f",  # 游戏编号
                 "game_type": "texas-holdem",  # 短牌模式
                 "players": [
                     {"id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078", "name": "ws_agent", "money": 1000.0},
                     {"id": "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47", "name": "1", "money": 1000.0}],
                 "dealer_id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078",  # 庄家
                 "big_blind": 40.0,
                 "small_blind": 20.0,
                 "event": "new-game"}  # 开始事件
            debug("[game start]")
            self.hand = []
            self.board = []
        elif event == "game-over":
            _ = {'message_type': 'game-update', 'event': 'game-over', 'game_id': '9c219ff9-616c-433b-adfd-04239af93275'}
            debug("[game over]")
        elif event == "cards-assignment":
            _ = {"message_type": "game-update",
                 "target": "ba05d6ac-e42b-4105-b3d5-4e26371dd078",  # 目标玩家
                 "cards": [[12, 3], [9, 1]],  # 底牌
                 "score": {"category": 0, "cards": [[12, 3], [9, 1]]},
                 "event": "cards-assignment",  # 发牌事件
                 "game_id": "35fc022f-468c-4e93-a069-a9da0e52526f"}
            category = msg["score"]["category"]
            cards = msg["score"]["cards"]
            self.hand = cards
            debug(f"[dealt] category:{category}, cards:{cards2str(self.hand)}")
        elif event == "player-action":
            _ = {"message_type": "game-update",
                 "action": "bet",  # 行动类型
                 "player": {"id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078", "name": "ws_agent", "money": 980.0},  # 玩家状态
                 "min_bet": 20.0,  # 下注最小值
                 "max_bet": 980.0,  # 下注最大值
                 "bets": {"ba05d6ac-e42b-4105-b3d5-4e26371dd078": 20.0, "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47": 40.0},  # 当前下注状态
                 "timeout": 30,  # 行动超时时长
                 "timeout_date": "2021-11-18 08:37:12+0000",  # 超时时间
                 "event": "player-action",  # 行动事件
                 "game_id": "35fc022f-468c-4e93-a069-a9da0e52526f"}
            _ = {'message_type': 'game-update',
                 'action': 'cards-change',
                 'player': {'id': '7d4c45ef-b059-4b58-9459-bd44efbf142a', 'name': 'ws_agent', 'money': 990.0},
                 'timeout': 30, 'timeout_date': '2021-11-19 03:04:18+0000',
                 'event': 'player-action', 'game_id': 'db804b66-8ffb-4eaf-a7ca-049d2bef4036'}
            pid = msg["player"]["id"]
            name = msg["player"]["name"]
            money = msg["player"]["money"]
            timeout = msg["timeout"]
            is_self = pid == self.pid
            debug(f"[crt] name:{name}, money:{money}, timeout:{timeout}, self:{is_self}")
            if is_self:
                act = {
                    "message_type": "bet",
                    "bet": msg["min_bet"]
                }
                self.ws.send(act)
                debug(f"[self] bet:{act['bet']}")
                # 自己行动反馈
                _ = {'message_type': 'game-update',
                     'player': {'id': '7101d05e-e862-45aa-a888-4603f6717005', 'name': 'ws_agent', 'money': 960.0},
                     'bet': 20,
                     'bet_type': 'call',  # 补齐视为call
                     'bets': {'7101d05e-e862-45aa-a888-4603f6717005': 40.0, '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': 40.0},
                     'event': 'bet',
                     'game_id': 'bbde7dea-74b2-4c71-a80a-6c4994a32eba'}
                # 轮到对方行动
                _ = {'message_type': 'game-update', 'action': 'bet',
                     'player': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0},
                     'min_bet': 0.0, 'max_bet': 960.0,
                     'bets': {'7101d05e-e862-45aa-a888-4603f6717005': 40.0, '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': 40.0},
                     'timeout': 30, 'timeout_date': '2021-11-18 09:01:34+0000',
                     'event': 'player-action', 'game_id': 'bbde7dea-74b2-4c71-a80a-6c4994a32eba'}
                # 对方行动反馈
                _ = {'message_type': 'game-update',
                     'player': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0},
                     'bet': 0,
                     'bet_type': 'check',
                     'bets': {'7101d05e-e862-45aa-a888-4603f6717005': 40.0, '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': 40.0},
                     'event': 'bet', 'game_id': 'bbde7dea-74b2-4c71-a80a-6c4994a32eba'}
        elif event == "cards-change":
            debug(f"msg:{msg}")
        elif event == "bet":
            _ = {"message_type": "game-update",
                 "player": {"id": "ba05d6ac-e42b-4105-b3d5-4e26371dd078", "name": "ws_agent", "money": 980.0},  # 玩家账户变化
                 "bet": 20.0,  # 加注值
                 "bet_type": "blind",  # 盲注
                 "bets": {"ba05d6ac-e42b-4105-b3d5-4e26371dd078": 20.0},  # 玩家加注状态
                 "event": "bet",  # 加注事件
                 "game_id": "35fc022f-468c-4e93-a069-a9da0e52526f"}
            _ = {"message_type": "game-update",
                 "player": {"id": "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47", "name": "1", "money": 960.0},  # 玩家账户变化
                 "bet": 40.0,  # 加注值
                 "bet_type": "blind",
                 "bets": {"ba05d6ac-e42b-4105-b3d5-4e26371dd078": 20.0, "714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47": 40.0},
                 "event": "bet",
                 "game_id": "35fc022f-468c-4e93-a069-a9da0e52526f"}
            pid = msg["player"]["id"]
            name = msg["player"]["name"]
            money = msg["player"]["money"]
            act = msg["bet_type"]
            bet = msg["bet"]
            debug(f"[act] name:{name}, money:{money}, act:{act}, bet:{bet}, self:{pid == self.pid}")
        elif event == "fold":
            _ = {'message_type': 'game-update',
                 'player': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0},
                 'event': 'fold', 'game_id': '5ed0d070-69d1-4a22-9232-fb221ed27a8e'}
            pid = msg["player"]["id"]
            name = msg["player"]["name"]
            is_self = pid == self.pid
            debug(f"[fold] pid:{pid}, name:{name}, is_self:{is_self}")
        elif event == "dead-player":
            _ = {'message_type': 'game-update',
                 'player': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0},
                 'event': 'dead-player', 'game_id': '9c219ff9-616c-433b-adfd-04239af93275'}
            name = msg["player"]["name"]
            debug(f"[offline] name:{name}")
        elif event == "showdown":
            _ = {'message_type': 'game-update',
                 'players': {
                     '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': {'cards': [[13, 1], [11, 1]], 'score': {'category': 0, 'cards': [[13, 1], [12, 3], [11, 1], [9, 0], [8, 2]]}},
                     '34c7df18-e538-4948-b2c8-9099f34bf143': {'cards': [[12, 1], [6, 1]], 'score': {'category': 1, 'cards': [[12, 3], [12, 1], [9, 0], [8, 2], [7, 2]]}}},
                 'event': 'showdown', 'game_id': '4e5d8eb0-3bf4-4679-ab45-d3f8124f2496'}
            for pid in msg["players"]:
                cards = msg["players"][pid]["cards"]
                board = msg["players"][pid]["score"]["cards"]
                debug(f"[showdown] pid:{pid}, cards:{cards2str(cards)}, board:{cards2str(board)}")
        elif event == "pots-update":
            _ = {'message_type': 'game-update',
                 'pots': [{'money': 40.0, 'player_ids': ['011fcb8d-4cb3-4734-a227-0e7292bb67d3']}],
                 'players': {
                     '011fcb8d-4cb3-4734-a227-0e7292bb67d3': {'id': '011fcb8d-4cb3-4734-a227-0e7292bb67d3', 'name': 'ws_agent', 'money': 960.0}},
                 'event': 'pots-update', 'game_id': 'a751bad5-c2de-4a84-aecf-b7010911af25'}
            _ = {'message_type': 'game-update',
                 'pots': [{'money': 80.0, 'player_ids': ['714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf']}],
                 'players': {
                     '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0},
                     'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf': {'id': 'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf', 'name': 'ws_agent', 'money': 960.0}},
                 'event': 'pots-update', 'game_id': '9c219ff9-616c-433b-adfd-04239af93275'}
            for pot in msg["pots"]:
                money = pot["money"]
                pids = pot["player_ids"]
                names = []
                for pid in pids:
                    name = msg["players"][pid]['name']
                    names.append(name)
                debug(f"[pot] money:{money}, names:{names}")
        elif event == "winner-designation":
            _ = {'message_type': 'game-update',
                 'pot': {'money': 80.0,
                         'player_ids': ['714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf'],
                         'winner_ids': ['f56595e2-cd98-4e9f-87a4-b3fbf5b44baf'],
                         'money_split': 80},
                 'pots': [],
                 'players': {
                     'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf': {'id': 'f56595e2-cd98-4e9f-87a4-b3fbf5b44baf', 'name': 'ws_agent', 'money': 1040.0}
                 },
                 'event': 'winner-designation', 'game_id': '9c219ff9-616c-433b-adfd-04239af93275'}
            _ = {'message_type': 'game-update',
                 'pot': {'money': 80.0,
                         'player_ids': ['714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', '34c7df18-e538-4948-b2c8-9099f34bf143'],
                         'winner_ids': ['34c7df18-e538-4948-b2c8-9099f34bf143'],
                         'money_split': 80},
                 'pots': [],
                 'players': {
                     '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0},
                     '34c7df18-e538-4948-b2c8-9099f34bf143': {'id': '34c7df18-e538-4948-b2c8-9099f34bf143', 'name': 'ws_agent', 'money': 1040.0}},
                 'event': 'winner-designation', 'game_id': '4e5d8eb0-3bf4-4679-ab45-d3f8124f2496'}
            _ = {'message_type': 'game-update',
                 'pot': {'money': 80.0,
                         'player_ids': ['f699eab7-a588-422f-8af3-b7a2289dc2e9'],
                         'winner_ids': ['f699eab7-a588-422f-8af3-b7a2289dc2e9'],
                         'money_split': 80},
                 'pots': [],
                 'players': {
                     'f699eab7-a588-422f-8af3-b7a2289dc2e9': {'id': 'f699eab7-a588-422f-8af3-b7a2289dc2e9', 'name': 'ws_agent', 'money': 1040.0}},
                 'event': 'winner-designation', 'game_id': 'ba1f3dde-1d3f-455f-867f-8c53fc254394'}
            _ = {'message_type': 'game-update',
                 'pot': {'money': 120.0,
                         'player_ids': ['70c5fd09-3273-4b67-b1ed-009080b71221', '6e27ad76-500d-4250-9ff7-b00e1e591388', '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47'],
                         'winner_ids': ['6e27ad76-500d-4250-9ff7-b00e1e591388'],
                         'money_split': 120},
                 'pots': [],
                 'players': {
                     '70c5fd09-3273-4b67-b1ed-009080b71221': {'id': '70c5fd09-3273-4b67-b1ed-009080b71221', 'name': 'ws_agent', 'money': 920.0},
                     '6e27ad76-500d-4250-9ff7-b00e1e591388': {'id': '6e27ad76-500d-4250-9ff7-b00e1e591388', 'name': 'ws_agent', 'money': 1120.0},
                     '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47': {'id': '714f1ad1-9726-4bb0-b2cd-8ecc1c53bb47', 'name': '1', 'money': 960.0}},
                 'event': 'winner-designation', 'game_id': '2c77ddf7-f729-4535-ac66-5b82a7589a4a'}

            winner_ids = msg["pot"]["winner_ids"]
            money_split = msg["pot"]["money_split"]
            ids_len = len(winner_ids)
            for pid in winner_ids:
                is_self = pid == self.pid
                debug(f"[done] pid:{pid}, add:{money_split / ids_len}, is_self:{is_self}")
            for pid in msg["players"]:
                name = msg["players"][pid]["name"]
                money = msg["players"][pid]["money"]
                is_self = pid == self.pid
                debug(f"[done] pid:{pid}, name:{name}, money:{money}, is_self:{is_self}")
            debug(f"[done] msg:{msg}")
        elif event == "shared-cards":
            _ = {'message_type': 'game-update',
                 'cards': [[8, 1], [10, 3], [2, 3]],
                 'event': 'shared-cards', 'game_id': '9c219ff9-616c-433b-adfd-04239af93275'}
            board = msg["cards"]
            self.board += board
            debug(f"[board] hand:{cards2str(self.hand)}, board:{cards2str(self.board)}")
        else:
            debug(f"unknown event.type:{event}")


if __name__ == "__main__":
    agent = Agent()
    agent.connect(ws_url)
