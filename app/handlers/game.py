import random
import httpx
import re
from urllib.parse import quote_plus
from telegram import Update
from telegram.ext import ContextTypes
from ..data_manager import user_language, user_selected_dict, get_words_from_dict
from ..texts import get_text
from ..config import DEFAULT_LANG, logger

async def fetch_definition(word: str, lang: str) -> str:
    """Fetches a brief definition from Wiktionary API."""
    url = f"https://{lang}.wiktionary.org/api/rest_v1/page/definition/{quote_plus(word)}"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                return None
            
            data = response.json()
            # Wiktionary returns a list of parts of speech
            # We take the first definition of the first part of speech
            for pos in data:
                if "definitions" in pos and pos["definitions"]:
                    first_def = pos["definitions"][0]["definition"]
                    # Clean up HTML tags from definition
                    clean_def = re.sub(r'<[^>]+>', '', first_def)
                    return clean_def.strip()
    except Exception as e:
        logger.error(f"Error fetching definition for {word}: {e}")
    return None

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

