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
        file_to_read = USER_DATA_FILE
        if not os.path.exists(file_to_read) and os.path.exists("user_data.json"):
            file_to_read = "user_data.json"

        if not os.path.exists(file_to_read):
            return {}, {}
        with open(file_to_read, 'r', encoding='utf-8') as f:
            data = json.load(f)
            user_language = {int(k): v for k, v in data.get("user_language", {}).items() if str(k).isdigit()}
            user_selected_dict = {int(k): v for k, v in data.get("user_selected_dict", {}).items() if str(k).isdigit()}
            return user_language, user_selected_dict
    except (FileNotFoundError, json.JSONDecodeError, IsADirectoryError, UnicodeDecodeError):
        logger.warning(f"Data file {USER_DATA_FILE} is missing, empty, or corrupted. Starting fresh.")
        return {}, {}

async def save_data(lang_data, dict_data):
    async with _save_lock:
        if os.path.isdir(USER_DATA_FILE):
            logger.error(f"FATAL: {USER_DATA_FILE} is a directory! Data NOT saved. Please delete the directory on host.")
            return

        lang_copy = {str(k): v for k, v in list(lang_data.items())}
        dict_copy = {str(k): v for k, v in list(dict_data.items())}
        
        def _save():
            directory = os.path.dirname(os.path.abspath(USER_DATA_FILE))
            if directory:
                os.makedirs(directory, exist_ok=True)
            tmp_file = f"{USER_DATA_FILE}.tmp"
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump({"user_language": lang_copy, "user_selected_dict": dict_copy}, f, indent=2, ensure_ascii=False)
            os.replace(tmp_file, USER_DATA_FILE)
        
        await asyncio.to_thread(_save)

async def get_available_dictionaries():
    if not os.path.exists(DICT_PATH):
        os.makedirs(DICT_PATH)
    files = await asyncio.to_thread(os.listdir, DICT_PATH)
    return sorted([f for f in files if f.endswith('.txt')])

async def get_words_from_dict(filename: str, count: int = 0):
    try:
        safe_filename = os.path.basename(filename)
        async with _words_cache_lock:
            words = WORDS_CACHE.get(safe_filename)
            if words is not None:
                WORDS_CACHE.move_to_end(safe_filename)

        if words is None:
            file_path = os.path.join(DICT_PATH, safe_filename)
            async with aiofiles.open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                words = []
                async for line in f:
                    stripped = line.strip()
                    if stripped:
                        words.append(stripped)
            words = await _cache_words(safe_filename, words)

        if count == 0:
            return words
        if not words:
            return []
        return random.sample(words, min(count, len(words)))
    except (FileNotFoundError, OSError):
        return []

def clear_cache(filename: str = None):
    safe_filename = os.path.basename(filename) if filename else None
    if safe_filename:
        WORDS_CACHE.pop(safe_filename, None)
        return
    WORDS_CACHE.clear()

user_language, user_selected_dict = load_data()
