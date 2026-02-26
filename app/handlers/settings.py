from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import NetworkError, BadRequest
import asyncio
import os
from ..config import DEFAULT_LANG, logger, DICT_PATH, is_admin
from ..texts import get_text
from ..data_manager import (user_language, user_selected_dict, save_data, 
                            WORDS_CACHE, get_available_dictionaries)
from .ui import (get_settings_reply_keyboard, get_dict_selection_inline_keyboard, 
                 get_lang_inline_keyboard)

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    keyboard = get_settings_reply_keyboard(lang)
    await update.message.reply_text(get_text('settings_menu_prompt', lang), reply_markup=keyboard)

async def handle_change_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    keyboard = await get_dict_selection_inline_keyboard("set_default_dict")
    reply_target = update.message or update.callback_query.message
    await reply_target.reply_text(get_text('available_dicts', lang), reply_markup=keyboard)

async def handle_change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    keyboard = get_lang_inline_keyboard()
    await update.message.reply_text(get_text('choose_lang_prompt', lang), reply_markup=keyboard)

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .common import show_main_menu_and_welcome
    query = update.callback_query
    try:
        await query.answer()
    except (NetworkError, BadRequest):
        return

    user_id = query.from_user.id
    data = query.data

    if data.startswith("set_lang:"):
        lang = data.split(":")[1]
        user_language[user_id] = lang
        await save_data(user_language, user_selected_dict)
        logger.info(f"User {user_id} set language to {lang}")
        await query.edit_message_text(get_text('choose_dict_prompt', lang))
        await handle_change_dict(update, context)
        return

    lang = user_language.get(user_id, DEFAULT_LANG)

    if data.startswith("addword_to_dict:"):
        if not is_admin(user_id):
            await query.edit_message_text(get_text('admin_only', lang))
            return ConversationHandler.END
            
        dict_name = data.split(":", 1)[1]
        words = context.user_data.get('words_to_add', [])
        if words:
            def append_words_to_file():
                with open(os.path.join(DICT_PATH, dict_name), 'a', encoding='utf-8') as f:
                    for word in words:
                        f.write(f"\n{word}")
            await asyncio.to_thread(append_words_to_file)
            
            if dict_name in WORDS_CACHE:
                del WORDS_CACHE[dict_name]

            await query.edit_message_text(get_text('addword_success', lang).format(dict_name=dict_name))
            context.user_data.clear()
            await show_main_menu_and_welcome(update, context)
        return ConversationHandler.END

    if data.startswith("set_default_dict:"):
        dict_name = data.split(":")[1]
        user_selected_dict[user_id] = dict_name
        await save_data(user_language, user_selected_dict)
        logger.info(f"User {user_id} set default dict to {dict_name}")
        await query.edit_message_text(get_text('dict_changed', lang).format(dict=dict_name), parse_mode='HTML')
        await show_main_menu_and_welcome(update, context)
        return
