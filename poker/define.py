MODE = "custom-poker:lobby"  # 自定义短牌
MODE_CUSTOM = "custom-poker:lobby"  # 自定义短牌
MODE_SHORT = "short-poker:lobby"  # 短牌
MODE_LONG = "long-poker:lobby"  # 长牌

SHOW_LOG = False  # 追踪日志

POTS = {  # 加注尺度
    "1/3 pot": 1 / 3,  # *倍底池
    "1/2 pot": 1 / 2,  # *倍底池
    "2/3 pot": 2 / 3,  # *倍底池
    "1 pot": 1,  # *倍底池
}

STACK_MULTI = 1000.0  # 筹码倍率
STACK_INIT = 200 * STACK_MULTI  # 初始筹码

TIMEOUT_TOLERANCE = 2  # 超时次数
# BET_TIMEOUT = 30  # 行动超时时间
BET_TIMEOUT = 60 * 60 * 24 * 365  # 行动超时时间
CHANGE_CARDS_TIMEOUT = 30  # unknown

WAIT_AFTER_CARDS_ASSIGNMENT = 1  # 等待秒数:发手牌
WAIT_AFTER_BET_ROUND = 1  # 等待秒数:加注轮
WAIT_AFTER_SHOWDOWN = 2  # 等待秒数:开牌
WAIT_AFTER_WINNER_DESIGNATION = 5  # 等待秒数:获奖
WAIT_AFTER_FLOP_TURN_RIVER = 1  # 等待秒数:发公牌
WAIT_AFTER_CARDS_CHANGE = 1  # unknown
