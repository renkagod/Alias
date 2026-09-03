import os
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from ..config import DEFAULT_LANG, DICT_PATH, is_admin
from ..texts import get_text
from ..data_manager import user_language, user_selected_dict, save_data, clear_cache
from .ui import get_dict_selection_inline_keyboard, get_main_reply_keyboard

AWAITING_WORDS, AWAITING_DICT_CHOICE = range(2)
AWAITING_DICT_FILE = 0

async def addword_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    if not is_admin(user_id):
        await update.message.reply_text(get_text('admin_only', lang))
        return ConversationHandler.END
    await update.message.reply_text(get_text('addword_prompt', lang), reply_markup=ReplyKeyboardRemove())
    return AWAITING_WORDS

async def addword_receive_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw_text = update.message.text or ""
    words = [line.strip() for line in raw_text.splitlines() if line.strip()]
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)

    if not words:
        await update.message.reply_text(get_text('addword_prompt', lang))
        return AWAITING_WORDS

    keyboard = await get_dict_selection_inline_keyboard("addword_to_dict")
    if not keyboard.inline_keyboard:
        await update.message.reply_text(
            get_text('no_dicts_available', lang), 
            reply_markup=get_main_reply_keyboard(lang)
        )
        return ConversationHandler.END

    context.user_data['words_to_add'] = words
    await update.message.reply_text(get_text('addword_choose_dict', lang), reply_markup=keyboard)
    return AWAITING_DICT_CHOICE

async def dict_upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    if not is_admin(user_id):
        await update.message.reply_text(get_text('admin_only', lang))
        return ConversationHandler.END
    await update.message.reply_text(get_text('upload_prompt', lang), reply_markup=ReplyKeyboardRemove())
    return AWAITING_DICT_FILE

async def dict_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from .common import show_main_menu_and_welcome
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    if not is_admin(user_id):
        await update.message.reply_text(get_text('admin_only', lang))
        return ConversationHandler.END
    
    document = update.message.document
    if document and document.file_name and document.file_name.endswith('.txt'):
        safe_name = os.path.basename(document.file_name)
        if not safe_name or safe_name == '.txt':
            await update.message.reply_text(get_text('invalid_file_type', lang))
            return AWAITING_DICT_FILE

        file = await document.get_file()
        file_path = os.path.join(DICT_PATH, safe_name)
        await file.download_to_drive(file_path)
        clear_cache(safe_name)
            
        user_selected_dict[user_id] = safe_name
        await save_data(user_language, user_selected_dict)
        await update.message.reply_text(get_text('upload_success', lang).format(filename=safe_name))
        await show_main_menu_and_welcome(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(get_text('invalid_file_type', lang))
        return AWAITING_DICT_FILE

