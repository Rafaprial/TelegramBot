import requests
import time
from app_parameters import Config

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load GPT-J 6B model from Hugging Face
model_name = "EleutherAI/gpt-j-6B"
model = AutoModelForCausalLM.from_pretrained(model_name, from_tf=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)

API_TOKEN = Config.url

BASE_URL = f'https://api.telegram.org/bot{API_TOKEN}'
# Create FastAPI instance

HELP_MESSAGE = """
📝 <b>Welcome to the Bot Help!</b>

Here are some commands you can send to the bot:

1. <b>ASK ANYTHING TO GPT</b>
   - <b>Description</b>: Get answers to all your questions.
   - <b>Example</b>: What is the capital of France? 
   - <b>Response</b>: The bot will respond with the answer to current question.

2. <b>HELP</b>
   - <b>Description</b>: Display this help message.
   - <b>Example</b>: <code>HELP</code>
   - <b>Response</b>: The bot will send you this help message showing available commands.

---

🌍 <b>All questions and answers will remain secret and will not be saved</b>:
  
If you need any other help, feel free to reach out! <a href="https://t.me/rfaaaaaaaaaaaaaaaaa">@rfaaaaaaaaaaaaaaaaa</a>
"""



# Can be moved to a util funct
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

def generate_response(prompt):
    # Encode the input prompt
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generate a response using the model
    with torch.no_grad():
        outputs = model.generate(inputs['input_ids'], max_length=150, num_return_sequences=1)
    
    # Decode and return the response
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Function to handle the bot updates in a separate thread
def gpt_bot_worker():
    offset = None  # To start from the latest update
    while True:
        updates = get_updates(offset)
        if updates['result']:
            message_id = get_last_update_id(updates)  # Get the last update ID
        
            for update in updates['result']:
                try:
                    chat_id = update['message']['chat']['id']
                    message_text = update['message']['text']
                    gpt_response = generate_response(message_text)
                    try:
                        send_message(chat_id, gpt_response)
                    except Exception as e:
                        send_message(chat_id, f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            # Update the offset to avoid reprocessing the same messages
            offset = message_id + 1
        
        # Wait for a short time before checking for new updates again
        time.sleep(1)