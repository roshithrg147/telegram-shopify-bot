# #########################
# Author: RR
# Email: roshithrag@gmail.com
# Created: 2025-05-30
# #########################

from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
if not (BOT_TOKEN := os.environ.get("BOT_TOKEN")):
    raise ValueError("BOT_TOKEN environment variable is not set!")
if not (OPENROUTER_API_KEY := os.environ.get("OPENROUTER_API_KEY")):
    raise ValueError("OPENROUTER_API_KEY environment variable is not set!")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


def handle_natural_conversation(text):
    """Handle natural language conversations using GPT"""
    try:
        # Create system prompt that defines the bot's role and knowledge
        system_prompt = """You are a helpful T-shirt store assistant. You help customers find the perfect t-shirt.
Available products:
- Classic fit t-shirts (XS to 2XL)
- Oversized t-shirts (S to XL)
- Graphic print t-shirts (anime, minimalist designs)
- Summer collection (breathable cotton)

Key information:
- Delivery: 3-5 business days (standard), 1-2 days (express)
- Size guide available
- Pan-India shipping
- Returns accepted within 7 days

Respond in a friendly, helpful manner. Focus on understanding the customer's needs and making relevant suggestions.
Never mention Telegram commands (starting with /).
Keep responses concise but informative."""

        # Get GPT's response
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://telegram-shopify-bot.onrender.com",
                "X-Title": "T-Shirt Store Bot"
            },
            model="anthropic/claude-2",  # Using Claude for natural conversations
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=150,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generating GPT response: {str(e)}")
        # Fallback response if GPT fails
        return "I'm here to help you find the perfect t-shirt! Could you tell me what style you're looking for?"


def setup_webhook(url):
    """Setup webhook for Telegram bot"""
    webhook_url = f"{url}/{BOT_TOKEN}"
    # First, delete any existing webhook
    delete_webhook_url = f"{API_URL}/deleteWebhook"
    requests.get(delete_webhook_url)

    # Set the new webhook
    set_webhook_url = f"{API_URL}/setWebhook?url={webhook_url}"
    response = requests.get(set_webhook_url)
    result = response.json()
    print(f"Webhook setup response: {result}")  # Log webhook setup result
    return result


@app.route('/')
def index():
    # Check webhook info
    webhook_info_url = f"{API_URL}/getWebhookInfo"
    webhook_info = requests.get(webhook_info_url).json()

    # Check if webhook is set correctly
    if not webhook_info.get('ok'):
        return f"Bot Status: 🔴 Error getting webhook info: {webhook_info}"
    webhook_data = webhook_info['result']
    return f"""Bot Status: 🟢 Live
Webhook URL: {webhook_data.get('url', 'Not set')}
Last Error: {webhook_data.get('last_error_message', 'None')}
Last Error Date: {webhook_data.get('last_error_date', 'Never')}
Max Connections: {webhook_data.get('max_connections', '40')}
Pending Updates: {webhook_data.get('pending_update_count', '0')}"""


@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    try:
        data = request.get_json()
        print(f"Received webhook data: {data}")  # Log incoming webhook data

        # Handle different types of updates
        if 'message' not in data:
            print("Received non-message update")
            return '', 200  # Acknowledge non-message updates

        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        # Handle commands
        if text.startswith('/'):
            if text == '/start':
                send_message(
                    chat_id, "👋 Welcome to our store! I'm here to help you find the perfect tee. What kind of style are you looking for?")
            elif text == '/browse':
                send_message(
                    chat_id, "🛍️ Our store catalog is coming soon! Meanwhile, tell me what you're looking for and I'll help you find it!")
            elif text == '/offers':
                send_message(
                    chat_id, "🏷️ No active offers at the moment, but I can help you find something that fits your style and budget! What are you looking for?")
            else:
                send_message(
                    chat_id, "I'm better at natural conversation! Just tell me what kind of t-shirt you're looking for, and I'll help you find it. 😊")
        else:
            # Handle natural conversation
            response = handle_natural_conversation(text)
            send_message(chat_id, response)

        return '', 200
    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        return '', 200  # Always return 200 to Telegram


if __name__ == '__main__':
    try:
        # Verify bot token is valid
        response = requests.get(f"{API_URL}/getMe")
        if not response.json().get('ok'):
            raise ValueError("Invalid BOT_TOKEN")

        port = int(os.environ.get("PORT", 5000))
        # Set up webhook for production
        webhook_url = "https://telegram-shopify-bot.onrender.com"
        setup_webhook(webhook_url)
        print("Bot is ready to receive messages!")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error starting bot: {str(e)}")
        raise
