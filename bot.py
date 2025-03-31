import requests
import time
import threading
from fastapi import FastAPI
from app_parameters import Config
from arbitrage_bot import bot_worker
# from gpt_bot import gpt_bot_worker

app = FastAPI()

# Start the bot in a separate thread when the FastAPI server starts
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=bot_worker, daemon=True).start()
#   WAITING FOR DATA
    # threading.Thread(target=gpt_bot_worker, daemon=True).start()

# FastAPI will now only handle the background worker and nothing else
