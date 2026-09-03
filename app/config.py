import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Пути к файлам и папкам
DICT_PATH = os.getenv("DICT_PATH", "dictionaries/")
USER_DATA_FILE = os.getenv("USER_DATA_FILE", "data/user_data.json")

# Настройки поведения
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ru").lower().strip()
if DEFAULT_LANG not in ("ru", "en"):
    DEFAULT_LANG = "ru"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Список ID админов
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = []
for item in admin_ids_str.split(","):
    cleaned = item.strip()
    if not cleaned:
        continue
    try:
        ADMIN_IDS.append(int(cleaned))
    except ValueError:
        pass

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    if not ADMIN_IDS:
        return False
    return user_id in ADMIN_IDS
