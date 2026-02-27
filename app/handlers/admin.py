import os
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from ..config import DEFAULT_LANG, DICT_PATH, is_admin
from ..texts import get_text
from ..data_manager import user_language, user_selected_dict, save_data, WORDS_CACHE
from .ui import get_dict_selection_inline_keyboard

AWAITING_WORDS, AWAITING_DICT_CHOICE = range(2)

async def addword_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    if not is_admin(user_id):
        await update.message.reply_text(get_text('admin_only', lang))
        return ConversationHandler.END
    await update.message.reply_text(get_text('addword_prompt', lang), reply_markup=ReplyKeyboardRemove())
    return AWAITING_WORDS

async def addword_receive_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['words_to_add'] = update.message.text.splitlines()
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    keyboard = await get_dict_selection_inline_keyboard("addword_to_dict")
    await update.message.reply_text(get_text('addword_choose_dict', lang), reply_markup=keyboard)
    return AWAITING_DICT_CHOICE

async def dict_upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    if not is_admin(user_id):
        await update.message.reply_text(get_text('admin_only', lang))
        return
    await update.message.reply_text(get_text('upload_prompt', lang), reply_markup=ReplyKeyboardRemove())

async def dict_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .common import show_main_menu_and_welcome
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    if not is_admin(user_id):
        await update.message.reply_text(get_text('admin_only', lang))
        return
    
    document = update.message.document
    if document and document.file_name.endswith('.txt'):
        file = await document.get_file()
        file_path = os.path.join(DICT_PATH, document.file_name)
        await file.download_to_drive(file_path)
        
        if document.file_name in WORDS_CACHE:
            del WORDS_CACHE[document.file_name]
            
        user_selected_dict[user_id] = document.file_name
        await save_data(user_language, user_selected_dict)
        await update.message.reply_text(get_text('upload_success', lang).format(filename=document.file_name))
        await show_main_menu_and_welcome(update, context)
    else:
        await update.message.reply_text(get_text('invalid_file_type', lang))

