import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..config import DEFAULT_LANG, logger
from ..texts import get_text, TEXTS
from ..data_manager import user_language, user_selected_dict
from .ui import get_lang_inline_keyboard, get_main_reply_keyboard
from .settings import handle_change_dict

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")
    
    if user.id not in user_language:
        await update.message.reply_html(
            TEXTS[DEFAULT_LANG]['welcome_new'].format(user=user.mention_html()),
            reply_markup=get_lang_inline_keyboard()
        )
        return

    lang = user_language.get(user.id, DEFAULT_LANG)
    if user.id not in user_selected_dict:
        await handle_change_dict(update, context)
    else:
        await show_main_menu_and_welcome(update, context)

async def show_main_menu_and_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    active_dict = user_selected_dict.get(user_id, "N/A")
    keyboard = get_main_reply_keyboard(lang)
    reply_target = update.message or update.callback_query.message
    await reply_target.reply_html(get_text('welcome_existing', lang).format(dict=active_dict), reply_markup=keyboard)

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from telegram.ext import ConversationHandler
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    await update.message.reply_text("Action canceled.", reply_markup=get_main_reply_keyboard(lang))
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)
