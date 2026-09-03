import logging
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, 
                          MessageHandler, filters, ConversationHandler)

from app.config import BOT_TOKEN, logger
from app.texts import TEXTS
from app.handlers.common import start, error_handler, cancel_conversation, show_main_menu_and_welcome
from app.handlers.game import handle_random_word, close_http_client
from app.handlers.settings import (show_settings_menu, handle_change_dict, 
                                 handle_change_lang, button_callback_handler)
from app.handlers.admin import (addword_start, addword_receive_words, 
                              dict_upload_start, dict_upload_handler,
                              AWAITING_WORDS, AWAITING_DICT_CHOICE, AWAITING_DICT_FILE)

async def on_shutdown(app: Application):
    await close_http_client()

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in .env file or environment!")

    application = Application.builder().token(BOT_TOKEN).post_shutdown(on_shutdown).build()

    # Filters for Reply Keyboard buttons
    RANDOM_WORD_FILTER = filters.Text([TEXTS['en']['btn_random_word'], TEXTS['ru']['btn_random_word']])
    SETTINGS_FILTER = filters.Text([TEXTS['en']['btn_settings'], TEXTS['ru']['btn_settings']])
    BACK_TO_GAME_FILTER = filters.Text([TEXTS['en']['btn_back_to_game'], TEXTS['ru']['btn_back_to_game']])

    # Basic handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(RANDOM_WORD_FILTER, handle_random_word))
    application.add_handler(MessageHandler(SETTINGS_FILTER, show_settings_menu))
    application.add_handler(MessageHandler(BACK_TO_GAME_FILTER, show_main_menu_and_welcome))

    # Admin & Word addition handlers
    addword_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addword", addword_start)],
        states={
            AWAITING_WORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, addword_receive_words)],
            AWAITING_DICT_CHOICE: [CallbackQueryHandler(button_callback_handler, pattern="^addword_to_dict:")],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )
    application.add_handler(addword_conv_handler)

    dict_upload_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("dict_upload", dict_upload_start)],
        states={
            AWAITING_DICT_FILE: [MessageHandler(filters.Document.ALL, dict_upload_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )
    application.add_handler(dict_upload_conv_handler)
    
    # Callback Query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("Starting bot (modular version)...")
    application.run_polling()

if __name__ == "__main__":
    main()
