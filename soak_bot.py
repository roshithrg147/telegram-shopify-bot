# #########################
# Author: RR
# Email: roshithrag@gmail.com
# Created: 2025-05-30
# #########################

from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
if not (BOT_TOKEN := os.environ.get("BOT_TOKEN")):
    raise ValueError("BOT_TOKEN environment variable is not set!")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


def setup_webhook(url):
    """Setup webhook for Telegram bot"""
    webhook_url = f"{url}/{BOT_TOKEN}"
    set_webhook_url = f"{API_URL}/setWebhook?url={webhook_url}"
    response = requests.get(set_webhook_url)
    return response.json()


@app.route('/')
def index():
    # Check webhook info
    webhook_info_url = f"{API_URL}/getWebhookInfo"
    webhook_info = requests.get(webhook_info_url).json()
    return f"Bot is Live! Webhook info: {webhook_info}"


@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text')

    if text == '/start':
        send_message(
            chat_id, "👋 Welcome to our store! Use /browse or /offers to get started.")

        return '', 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Set up webhook for production
    webhook_url = "https://telegram-shopify-bot.onrender.com"
    setup_webhook(webhook_url)
    app.run(host='0.0.0.0', port=port)
