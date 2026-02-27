from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from ..texts import get_text
from ..data_manager import get_available_dictionaries

def get_main_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    keyboard = [
        [get_text('btn_random_word', lang)],
        [get_text('btn_settings', lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_settings_inline_keyboard(lang: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(get_text('btn_change_lang', lang), callback_data="settings_lang"),
            InlineKeyboardButton(get_text('btn_change_dict', lang), callback_data="settings_dict")
        ],
        [InlineKeyboardButton(get_text('btn_close', lang), callback_data="settings_close")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lang_inline_keyboard(action_prefix: str = "set_lang") -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton("🇬🇧 English", callback_data=f"{action_prefix}:en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data=f"{action_prefix}:ru")
    ]]
    return InlineKeyboardMarkup(keyboard)

async def get_dict_selection_inline_keyboard(action_prefix: str) -> InlineKeyboardMarkup:

    dictionaries = await get_available_dictionaries()
    keyboard = [[InlineKeyboardButton(d.replace('.txt', ''), callback_data=f"{action_prefix}:{d}")] for d in dictionaries]
    return InlineKeyboardMarkup(keyboard)
