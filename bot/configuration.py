import os

from dotenv import load_dotenv
from pathlib import Path
from config.settings import BASE_DIR

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

USER_IDS = [int(user) for user in os.getenv("USERS_ID").split(',')]