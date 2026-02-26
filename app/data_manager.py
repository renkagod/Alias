import os
import json
import asyncio
import random
import aiofiles
from .config import USER_DATA_FILE, DICT_PATH, logger

# Кэш для слов
WORDS_CACHE = {}
_save_lock = asyncio.Lock()

def load_data():
    try:
        if not os.path.exists(USER_DATA_FILE):
            # Если файла нет вообще, возвращаем пустые данные
            return {}, {}
        with open(USER_DATA_FILE, 'r') as f:
            data = json.load(f)
            # Приведение ключей (ID пользователей) к int
            user_language = {int(k): v for k, v in data.get("user_language", {}).items()}
            user_selected_dict = {int(k): v for k, v in data.get("user_selected_dict", {}).items()}
            return user_language, user_selected_dict
    except (FileNotFoundError, json.JSONDecodeError, IsADirectoryError):
        # Если это папка (ошибка докера) или файл пуст/отсутствует
        logger.warning(f"Data file {USER_DATA_FILE} is missing, empty, or a directory. Starting fresh.")
        return {}, {}

async def save_data(lang_data, dict_data):
    async with _save_lock:
        # Создаем копии для потокобезопасности
        lang_copy = {str(k): v for k, v in lang_data.items()}
        dict_copy = {str(k): v for k, v in dict_data.items()}
        
        def _save():
            os.makedirs(os.path.dirname(os.path.abspath(USER_DATA_FILE)) or '.', exist_ok=True)
            with open(USER_DATA_FILE, 'w') as f:
                json.dump({"user_language": lang_copy, "user_selected_dict": dict_copy}, f, indent=4)
        
        await asyncio.to_thread(_save)

async def get_available_dictionaries():
    if not os.path.exists(DICT_PATH):
        os.makedirs(DICT_PATH)
    # Используем run_in_executor для листинга директории
    files = await asyncio.to_thread(os.listdir, DICT_PATH)
    return sorted([f for f in files if f.endswith('.txt')])

async def get_words_from_dict(filename: str, count: int = 0):
    try:
        if filename in WORDS_CACHE:
            words = WORDS_CACHE[filename]
        else:
            file_path = os.path.join(DICT_PATH, filename)
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            words = [line.strip() for line in content.splitlines() if line.strip()]
            WORDS_CACHE[filename] = words

        if count == 0:
            return words
        return random.sample(words, min(count, len(words)))
    except FileNotFoundError:
        return []

def clear_cache(filename: str = None):
    if filename:
        if filename in WORDS_CACHE:
            del WORDS_CACHE[filename]
    else:
        WORDS_CACHE.clear()

user_language, user_selected_dict = load_data()
