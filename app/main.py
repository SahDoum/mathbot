from settings import WEBHOOK_URL, WEBHOOK_URL_PATH, PUB_CERT
from utils import bot

from flask import Flask, request, abort, jsonify
from redis import StrictRedis


# === Flask settings and routes ===
app = Flask(__name__)
r = StrictRedis('redis')


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        r.lpush('bot_queue', json_string)
        return ''
    else:
        abort(403)


@app.route(f'{WEBHOOK_URL_PATH}/set', methods=['GET'])
def set_webhook():
    cert = open(PUB_CERT, 'r') if PUB_CERT else None
    response = bot.set_webhook(WEBHOOK_URL, cert)
    return str(response)


@app.route(f'{WEBHOOK_URL_PATH}/delete', methods=['GET'])
def delete_webhook():
    response = bot.delete_webhook()
    return str(response)


@app.route(f'{WEBHOOK_URL_PATH}/info', methods=['GET'])
def get_info():
    return jsonify(str(bot.get_webhook_info()))
