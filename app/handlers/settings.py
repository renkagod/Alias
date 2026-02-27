from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import NetworkError, BadRequest
import asyncio
import os
from ..config import DEFAULT_LANG, logger, DICT_PATH, is_admin
from ..texts import get_text
from ..data_manager import (user_language, user_selected_dict, save_data, 
                            WORDS_CACHE, get_available_dictionaries)
from .ui import (get_settings_inline_keyboard, get_dict_selection_inline_keyboard, 
                 get_lang_inline_keyboard)

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    active_dict = user_selected_dict.get(user_id, "N/A")
    lang_name = "🇷🇺 Русский" if lang == "ru" else "🇬🇧 English"
    
    text = get_text('settings_info', lang).format(
        lang_name=lang_name,
        dict_name=active_dict
    )
    keyboard = get_settings_inline_keyboard(lang)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await update.message.reply_html(text, reply_markup=keyboard)

async def handle_change_dict(update: Update, context: ContextTypes.DEFAULT_TYPE, is_inline=False):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    keyboard = await get_dict_selection_inline_keyboard("set_default_dict")
    
    # Add a back button to settings if it's coming from settings
    if is_inline:
        keyboard.inline_keyboard.append([InlineKeyboardButton(get_text('btn_back_to_game', lang), callback_data="settings_back")])

    reply_target = update.message or update.callback_query.message
    if update.callback_query:
        await update.callback_query.edit_message_text(get_text('available_dicts', lang), reply_markup=keyboard)
    else:
        await reply_target.reply_text(get_text('available_dicts', lang), reply_markup=keyboard)

async def handle_change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    keyboard = get_lang_inline_keyboard("set_lang")
    keyboard.inline_keyboard.append([InlineKeyboardButton(get_text('btn_back_to_game', lang), callback_data="settings_back")])
    
    if update.callback_query:
        await update.callback_query.edit_message_text(get_text('choose_lang_prompt', lang), reply_markup=keyboard)
    else:
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

    if data == "settings_lang":
        await handle_change_lang(update, context)
        return
    
    if data == "settings_dict":
        await handle_change_dict(update, context, is_inline=True)
        return
    
    if data == "settings_back":
        await show_settings_menu(update, context)
        return

    if data == "settings_close":
        await query.delete_message()
        return

    if data.startswith("set_lang:"):
        lang = data.split(":")[1]
        user_language[user_id] = lang
        await save_data(user_language, user_selected_dict)
        logger.info(f"User {user_id} set language to {lang}")
        
        # If it was an initial setup, proceed to dict choice
        if not user_selected_dict.get(user_id):
            await query.edit_message_text(get_text('choose_dict_prompt', lang))
            await handle_change_dict(update, context)
        else:
            await show_settings_menu(update, context)
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
