import requests
import time
import threading
from fastapi import FastAPI

# Define constants for Telegram and Kraken API


API_TOKEN = '7778114116:AAG55hOR94R5Ol-5NE_2JVL4poMOZg0bAHU'
KRAKEN = "https://api.kraken.com/0/public/Ticker?pair="

BASE_URL = f'https://api.telegram.org/bot{API_TOKEN}'
# Create FastAPI instance
app = FastAPI()

HELP_MESSAGE = """
📝 <b>Welcome to the Bot Help!</b>

Here are some commands you can send to the bot:

1. <b>PRICE <code>currency_pair</code></b>
   - <b>Description</b>: Get the current price of a specific cryptocurrency.
   - <b>Example</b>: <code>PRICE BTC/USD</code> or <code>PRICE ETHEUR</code>
   - <b>Response</b>: The bot will respond with the current price of the given currency pair.

2. <b>HELP</b>
   - <b>Description</b>: Display this help message.
   - <b>Example</b>: <code>HELP</code>
   - <b>Response</b>: The bot will send you this help message showing available commands.

---

🌍 <b>Supported Currency Pairs</b>:
- The bot supports the following currencies: Bitcoin (BTC), Ethereum (ETH), and others available on Kraken API.
  
If you need any other help, feel free to reach out! <a href="https://t.me/rfaaaaaaaaaaaaaaaaa">@rfaaaaaaaaaaaaaaaaa</a>
"""



# Function to send a message to the user via Telegram
def send_message(chat_id: int, text: str):
    url = f'{BASE_URL}/sendMessage'
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    response = requests.get(url, params=params).json()
    # if reponse.json()
    if response['ok'] == False:

        print(f"Error: {response['description']}")
    else:

        return response

# Function to get updates from Telegram
def get_updates(offset=None):
    url = f'{BASE_URL}/getUpdates'
    params = {'offset': offset}  # Pass offset to get new updates after the last one
    response = requests.get(url, params=params)
    return response.json()

# Function to get the last update's ID
def get_last_update_id(updates):
    if len(updates['result']) > 0:
        return updates['result'][-1]['update_id']
    return None

# Function to get price by pair from Kraken API
def get_price_by_code(pair1: str, pair2: str = ""):
    return requests.get(f"{KRAKEN}{pair1}{pair2}").json()

# Function to handle the bot updates in a separate thread
def bot_worker():
    offset = None  # To start from the latest update
    while True:
        updates = get_updates(offset)
        
        if updates['result']:
            message_id = get_last_update_id(updates)  # Get the last update ID
        
            for update in updates['result']:
                try:
                    chat_id = update['message']['chat']['id']
                    message_text = update['message']['text']
                    if message_text.upper() == "/START":
                        send_message(chat_id, HELP_MESSAGE)
                        
                    # Respond to specific message like "PRICE"
                    elif "PRICE" in message_text.upper():
                        price = message_text.split(" ")[1]
                        try:
                            if "/" in price:
                                pair1, pair2 = price.split("/")
                                price = get_price_by_code(pair1, pair2)
                            else:
                                price = get_price_by_code(price)
                            price_name = list(price['result'].keys())[0]
                            send_message(chat_id, f"{price_name} : {price['result'][price_name]['c'][0]}")
                        except Exception as e:
                            send_message(chat_id, f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            # Update the offset to avoid reprocessing the same messages
            offset = message_id + 1
        
        # Wait for a short time before checking for new updates again
        time.sleep(1)

# Start the bot in a separate thread when the FastAPI server starts
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=bot_worker, daemon=True).start()

# FastAPI will now only handle the background worker and nothing else
