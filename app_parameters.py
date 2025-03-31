import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    url = os.getenv('BOTAPIKEY', '')
    gpt_api_token = os.getenv('GPTBOTAPIKEY', '')

config = Config()