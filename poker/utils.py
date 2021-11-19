import sys
import os
import time


def my_format(level, line, deep):
    f_lineno = sys._getframe(deep).f_lineno
    co_name = sys._getframe(deep).f_code.co_name
    co_filename = sys._getframe(deep).f_code.co_filename
    (_, filename) = os.path.split(co_filename)
    if level == "INFO":
        fore = "绿色"
    elif level == "WARNING":
        fore = "黄色"
    elif level == "ERROR":
        fore = "红色"
    elif level == "DEBUG":
        fore = ""
    else:
        fore = ""
    line = use_style(f"{level} {filename} {co_name}:{f_lineno} - {line}", fore=fore)
    return line


mark_count = 0


def mark(deep=0):
    global mark_count
    print(my_format("INFO", f"[MARK] {mark_count}", deep + 2))
    mark_count += 1


def info(line="", deep=0):
    print(my_format("INFO", line, deep + 2))


def warning(line="", deep=0):
    print(my_format("WARNING", line, deep + 2))


def error(line="", deep=0):
    print(my_format("ERROR", line, deep + 2))


def debug(line="", deep=0):
    print(my_format("DEBUG", line, deep + 2))


def head_tail(fn):
    def around(*args, **kwargs):
        func = fn.__name__
        info(f"=== {func} ===")
        res = fn(*args, **kwargs)
        info(f"--- {func} ---")
        return res

    return around


STYLE = {
    'fore': {
        "紫色": 30, "红色": 31, "绿色": 32, "紫红": 33, "青色": 34, "黄色": 35, "蓝色": 36, "灰色": 37,
        'black': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37,
    },
    'back': {
        "紫色": 30, "红色": 31, "绿色": 32, "紫红": 33, "青色": 34, "黄色": 35, "蓝色": 36, "灰色": 37,
        'black': 40, 'red': 41, 'green': 42, 'yellow': 43, 'blue': 44, 'purple': 45, 'cyan': 46, 'white': 47,
    },
    'mode': {
        'bold': 1, 'underline': 4, 'blink': 5, 'invert': 7,
    },
    'default': {
        'end': 0,
    }
}


# desc:
#   info: 字符串
#   mode: 模式
#   fore: 字的颜色
#   back: 背景颜色

def use_style(line, mode='', fore='', back=''):
    mode = '%s' % STYLE['mode'][mode] if mode in STYLE['mode'] else ''
    fore = '%s' % STYLE['fore'][fore] if fore in STYLE['fore'] else ''
    back = '%s' % STYLE['back'][back] if back in STYLE['back'] else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end = '\033[%sm' % STYLE['default']['end'] if style else ''
    return '%s%s%s' % (style, line, end)


def card2str(card_idx, color_idx):
    cards = "__23456789TJQKA"
    colors = ["红色", "蓝色", "黄色", "绿色"]
    card = use_style(cards[card_idx], fore=colors[color_idx])
    return card


def cards2str(hand):
    line = ""
    for card in hand:
        line += card2str(card[0], card[1])
    return line
