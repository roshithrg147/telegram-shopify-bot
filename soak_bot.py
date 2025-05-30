# #########################
# Author: RR
# Email: roshithrag@gmail.com
# Created: 2025-05-30
# #########################

from flask import Flask, request
import requests
import os

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL=f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route('/')
def index():
    return "Bot is Live!!"

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text')
    
    if text == '/start':
        send_message(chat_id, "👋 Welcome to our store! Use /browse or /offers to get started.")
        
        return '', 200
    
    def send_message(chat_id, text):
        url = f"{API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, json=payload)
        
    if __name__ == '__main__':
        app.run(debug=True)