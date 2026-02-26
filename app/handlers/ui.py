from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from ..texts import get_text
from ..data_manager import get_available_dictionaries

def get_main_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    keyboard = [
        [get_text('btn_random_word', lang)],
        [get_text('btn_settings', lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_settings_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    keyboard = [
        [get_text('btn_change_dict', lang), get_text('btn_change_lang', lang)],
        [get_text('btn_back_to_game', lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_lang_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru")
    ]]
    return InlineKeyboardMarkup(keyboard)

async def get_dict_selection_inline_keyboard(action_prefix: str) -> InlineKeyboardMarkup:
    dictionaries = await get_available_dictionaries()
    keyboard = [[InlineKeyboardButton(d.replace('.txt', ''), callback_data=f"{action_prefix}:{d}")] for d in dictionaries]
    return InlineKeyboardMarkup(keyboard)
