import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file or environment!")

# Пути к файлам и папкам
DICT_PATH = os.getenv("DICT_PATH", "dictionaries/")
USER_DATA_FILE = os.getenv("USER_DATA_FILE", "user_data.json")

# Настройки поведения
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ru")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Список ID админов
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_str.split(",") if i.strip()]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    if not ADMIN_IDS:
        return True
    return user_id in ADMIN_IDS
