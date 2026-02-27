import random
from urllib.parse import quote_plus
from telegram import Update
from telegram.ext import ContextTypes
from ..data_manager import user_language, user_selected_dict, get_words_from_dict
from ..texts import get_text
from ..config import DEFAULT_LANG

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
        await update.message.reply_html(f"{get_text('random_word_title', lang)} <a href='{dictionary_link}'><b>{word_text}</b></a>")
    else:
        await update.message.reply_text(get_text('no_words_in_dict', lang))
