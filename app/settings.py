import os
import logging

DEBUG = os.getenv('DEBUG', True)

API_TOKEN = os.getenv('SOSISKA_TOKEN', '')
BOT_NAME = os.getenv('BOT_NAME', '')

LOGGING_LEVEL = int(os.getenv('LOGGING_LEVEL', logging.INFO))
CHANNEL_NAME = os.getenv('CHANNEL_NAME', '')

IUMURL = "http://ium.mccme.ru/"

# Webhook settings
PUB_CERT = os.getenv('PUB_CERT', '')
WEBHOOK_HOST = os.getenv('HOST', '')
WEBHOOK_URL_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_URL_PATH}'
