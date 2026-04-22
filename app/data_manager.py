import os
import json
import asyncio
import random
from collections import OrderedDict
import aiofiles
from .config import USER_DATA_FILE, DICT_PATH, logger

# Кэш для слов
MAX_WORDS_CACHE_SIZE = 20
WORDS_CACHE: OrderedDict[str, list[str]] = OrderedDict()
_save_lock = asyncio.Lock()
_words_cache_lock = asyncio.Lock()


async def _cache_words(filename: str, words: list[str]) -> list[str]:
    async with _words_cache_lock:
        cached_words = WORDS_CACHE.get(filename)
        if cached_words is not None:
            WORDS_CACHE.move_to_end(filename)
            return cached_words

        WORDS_CACHE[filename] = words
        while len(WORDS_CACHE) > MAX_WORDS_CACHE_SIZE:
            WORDS_CACHE.popitem(last=False)
        return words

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
        # Если вдруг на хосте папка с таким именем (косяк докера)
        if os.path.isdir(USER_DATA_FILE):
            logger.error(f"FATAL: {USER_DATA_FILE} is a directory! Data NOT saved. Please delete the directory on host.")
            return

        # Создаем копии для потокобезопасности
        lang_copy = {str(k): v for k, v in lang_data.items()}
        dict_copy = {str(k): v for k, v in dict_data.items()}
        
        def _save():
            directory = os.path.dirname(os.path.abspath(USER_DATA_FILE))
            if directory:
                os.makedirs(directory, exist_ok=True)
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
        async with _words_cache_lock:
            words = WORDS_CACHE.get(filename)
            if words is not None:
                WORDS_CACHE.move_to_end(filename)

        if words is None:
            file_path = os.path.join(DICT_PATH, filename)
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                words = []
                async for line in f:
                    stripped = line.strip()
                    if stripped:
                        words.append(stripped)
            words = await _cache_words(filename, words)

        if count == 0:
            return words
        return random.sample(words, min(count, len(words)))
    except FileNotFoundError:
        return []

async def clear_cache(filename: str = None):
    async with _words_cache_lock:
        if filename:
            WORDS_CACHE.pop(filename, None)
            return
        WORDS_CACHE.clear()

user_language, user_selected_dict = load_data()
