import random
import httpx
import re
from urllib.parse import quote_plus
from telegram import Update
from telegram.ext import ContextTypes
from ..data_manager import user_language, user_selected_dict, get_words_from_dict
from ..texts import get_text
from ..config import DEFAULT_LANG, logger

async def fetch_definition_ru(word: str) -> str:
    """Fetches definition from Russian Wiktionary using MediaWiki Action API."""
    url = f"https://ru.wiktionary.org/w/api.php?action=query&prop=extracts&titles={quote_plus(word)}&format=json"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                if "-1" in pages:
                    # Try capitalized
                    url_cap = f"https://ru.wiktionary.org/w/api.php?action=query&prop=extracts&titles={quote_plus(word.capitalize())}&format=json"
                    response = await client.get(url_cap)
                    if response.status_code == 200:
                        data = response.json()
                        pages = data.get("query", {}).get("pages", {})

                page = next(iter(pages.values()), {})
                html = page.get("extract", "")
                
                if html:
                    match = re.search(r'<h4[^>]*>Значение</h4>\s*<ol>(.*?)</ol>', html, re.DOTALL)
                    if match:
                        list_items = re.findall(r'<li[^>]*>(.*?)</li>', match.group(1), re.DOTALL)
                        for item in list_items:
                            text = re.sub(r'<[^>]+>', '', item)
                            parts = text.split('◆')
                            if parts:
                                clean_def = parts[0].strip()
                                if clean_def and not clean_def.startswith("Отсутствует пример"):
                                    clean_def = re.sub(r'\s+', ' ', clean_def)
                                    return clean_def
    except Exception as e:
        logger.error(f"Error fetching RU definition for {word}: {e}")
    return None

async def fetch_definition_en(word: str) -> str:
    """Fetches definition from English Wiktionary using REST API."""
    url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{quote_plus(word)}"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            
            if response.status_code == 404:
                url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{quote_plus(word.capitalize())}"
                response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                lang_data = data.get("en", [])
                if not lang_data and data:
                    lang_data = next(iter(data.values()))

                for pos in lang_data:
                    if isinstance(pos, dict) and "definitions" in pos:
                        for definition_obj in pos["definitions"]:
                            if "definition" in definition_obj:
                                raw_def = definition_obj["definition"]
                                clean_def = re.sub(r'<[^>]+>', '', raw_def)
                                clean_def = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', clean_def)
                                clean_def = clean_def.strip()
                                if clean_def:
                                    return clean_def
    except Exception as e:
        logger.error(f"Error fetching EN definition for {word}: {e}")
    return None

async def fetch_definition(word: str, lang: str) -> str:
    word = word.strip().lower()
    if lang == 'ru':
        return await fetch_definition_ru(word)
    return await fetch_definition_en(word)

async def handle_random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .settings import handle_change_dict
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    active_dict = user_selected_dict.get(user_id)

    if not active_dict:
        await handle_change_dict(update, context)
        return

    word = await get_words_from_dict(active_dict, 1)
    if word:
        word_text = word[0]
        dictionary_link = f"https://{lang}.wiktionary.org/wiki/{quote_plus(word_text)}"
        
        # Try to get definition
        definition = await fetch_definition(word_text, lang)
        
        message_text = f"{get_text('random_word_title', lang)} <a href='{dictionary_link}'><b>{word_text}</b></a>"
        
        if definition:
            message_text += f"\n\n<tg-spoiler>📖 <b>{get_text('definition_title', lang)}:</b>\n{definition}</tg-spoiler>"
        
        await update.message.reply_html(message_text)
    else:
        await update.message.reply_text(get_text('no_words_in_dict', lang))

