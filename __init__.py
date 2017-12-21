import re
import logging
import telebot
from settings import API_TOKEN2

import sys
sys.path.append("../statistics display")
import bot_statistics as statistics

BOT_NAME = '@sosiska_v_teste_bot'
statistics.init_track(BOT_NAME)


# Command list handler function
def commands_handler(cmnds, inline=False):

    def wrapped(msg):
        if not msg.text:
            return False

        split_message = re.split(r'[^\w@\/]', msg.text)
        if not inline:
            s = split_message[0]
            result = (s in cmnds) or (s.endswith(BOT_NAME) and s.split('@')[0] in cmnds)
        else:
            result = any(cmnd in split_message or cmnd + BOT_NAME in split_message for cmnd in cmnds)

        if result:
            statistics.track_by_message(BOT_NAME, 'Command: ' + cmnds[0], msg)
        return result

    return wrapped


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN2, threaded=False)