import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    url = os.getenv('BOTAPIKEY', '')

config = Config()