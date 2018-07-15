import os
import logging

API_TOKEN = os.getenv('API_TOKEN', '')
BOT_NAME = os.getenv('BOT_NAME', '')

LOGGING_LEVEL = int(os.getenv('LOGGING_LEVEL', logging.INFO))
CHANNEL_NAME = os.getenv('CHANNEL_NAME', '')

IUMURL = "http://ium.mccme.ru/"
