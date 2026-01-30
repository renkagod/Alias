import os
import asyncio
import logging
import random
from io import BytesIO
from urllib.parse import quote_plus
from dotenv import load_dotenv
from telegram.error import NetworkError, BadRequest
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
                          filters, ContextTypes, ConversationHandler)

# --- CONFIGURATION / НАСТРОЙКИ ---
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file!")

DICT_PATH = "dictionaries/"
USER_DATA_FILE = "user_data.json"

# --- TEXTS FOR LOCALIZATION (Убраны ключи для кнопки "Несколько слов") ---
TEXTS = {
    'en': {
        'welcome_new': "👋 Hi, {user}!\n\nLooks like you're new here. Please choose your language:",
        'welcome_existing': "Your active dictionary: <b>{dict}</b>\n\nPress the button to get a word.",
        'choose_dict_prompt': "Great! Now choose a default dictionary:",
        'available_dicts': "Available dictionaries:",
        'dict_changed': "✅ Default dictionary changed to: <b>{dict}</b>.",
        'lets_start': "Let's begin! Use the buttons on the keyboard.",
        'no_dict_selected': "Please select a dictionary first! Go to Settings -> Change Dictionary.",
        'no_words_in_dict': "There are no words in this dictionary!",
        'random_word_title': "🎲 Word:",
        'btn_random_word': "🎲 Random Word",
        'btn_settings': "⚙️ Settings",
        'btn_change_dict': "📚 Change Dictionary",
        'btn_change_lang': "🌐 Change Language",
        'btn_back_to_game': "⬅️ Back to Game",
        'choose_lang_prompt': "Please choose your language:",
        'settings_menu_prompt': "⚙️ Settings Menu",
        'upload_prompt': "Send me a `.txt` file with words, each on a new line.",
        'upload_success': "✅ Dictionary `{filename}` uploaded and set as active.",
        'addword_prompt': "Send me the word(s) you want to add.",
        'addword_choose_dict': "Which dictionary to add the word(s) to?",
        'addword_success': "✅ Word(s) added to `{dict_name}`.",
    },
    'ru': {
        'welcome_new': "👋 Привет, {user}!\n\nПохоже, ты здесь впервые. Пожалуйста, выбери язык:",
        'welcome_existing': "Твой активный словарь: <b>{dict}</b>\n\nНажми на кнопку, чтобы получить слово.",
        'choose_dict_prompt': "Отлично! Теперь выбери словарь по умолчанию:",
        'available_dicts': "Доступные словари:",
        'dict_changed': "✅ Словарь по умолчанию изменён на: <b>{dict}</b>.",
        'lets_start': "Теперь можно начинать! Используй кнопки на клавиатуре.",
        'no_dict_selected': "Сначала нужно выбрать словарь! Зайди в Настройки -> Сменить словарь.",
        'no_words_in_dict': "В этом словаре нет слов!",
        'random_word_title': "🎲 Слово:",
        'btn_random_word': "🎲 Случайное слово",
        'btn_settings': "⚙️ Настройки",
        'btn_change_dict': "📚 Сменить словарь",
        'btn_change_lang': "🌐 Сменить язык",
        'btn_back_to_game': "⬅️ Назад в игру",
        'choose_lang_prompt': "Пожалуйста, выберите язык:",
        'settings_menu_prompt': "⚙️ Меню настроек",
        'upload_prompt': "Отправьте мне файл `.txt` со словами, каждое на новой строке.",
        'upload_success': "✅ Словарь `{filename}` загружен и установлен как активный.",
        'addword_prompt': "Отправьте мне слово (или слова), которые нужно добавить.",
        'addword_choose_dict': "В какой словарь добавить слова?",
        'addword_success': "✅ Слова добавлены в словарь `{dict_name}`.",
    }
}

# --- DATA MANAGEMENT ---
def load_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            data = json.load(f)
            user_language = {int(k): v for k, v in data.get("user_language", {}).items()}
            user_selected_dict = {int(k): v for k, v in data.get("user_selected_dict", {}).items()}
            return user_language, user_selected_dict
    except (FileNotFoundError, json.JSONDecodeError):
        return {}, {}

def save_data(lang_data, dict_data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump({"user_language": lang_data, "user_selected_dict": dict_data}, f, indent=4)

user_language, user_selected_dict = load_data()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- HELPER FUNCTIONS ---
def get_text(key: str, lang: str, default: str = None):
    return TEXTS.get(lang, TEXTS['en']).get(key, default or f"<{key}>")

def get_available_dictionaries():
    if not os.path.exists(DICT_PATH):
        os.makedirs(DICT_PATH)
    return [f for f in os.listdir(DICT_PATH) if f.endswith('.txt')]

def get_words_from_dict(filename: str, count: int = 0):
    try:
        with open(os.path.join(DICT_PATH, filename), 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        if count == 0:
            return words
        return random.sample(words, min(count, len(words)))
    except FileNotFoundError:
        return []

# --- KEYBOARD GENERATORS ---

def get_main_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    # Убрана кнопка "Несколько слов"
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

def get_dict_selection_inline_keyboard(action_prefix: str) -> InlineKeyboardMarkup:
    dictionaries = get_available_dictionaries()
    keyboard = [[InlineKeyboardButton(d.replace('.txt', ''), callback_data=f"{action_prefix}:{d}")] for d in dictionaries]
    return InlineKeyboardMarkup(keyboard)

# --- MESSAGE HANDLERS FOR REPLY KEYBOARD ---

async def handle_random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    active_dict = user_selected_dict.get(user_id)

    if not active_dict:
        await update.message.reply_text(get_text('no_dict_selected', lang))
        return

    word = get_words_from_dict(active_dict, 1)
    if word:
        word_text = word[0]
        dictionary_link = f"https://{lang}.wiktionary.org/wiki/{quote_plus(word_text)}"
        await update.message.reply_html(f"{get_text('random_word_title', lang)} <a href='{dictionary_link}'><b>{word_text}</b></a>")
    else:
        await update.message.reply_text(get_text('no_words_in_dict', lang))

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    keyboard = get_settings_reply_keyboard(lang)
    await update.message.reply_text(get_text('settings_menu_prompt', lang), reply_markup=keyboard)

async def show_main_menu_and_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    active_dict = user_selected_dict.get(user_id, "N/A")
    keyboard = get_main_reply_keyboard(lang)
    # Используем тот же самый приём
    reply_target = update.message or update.callback_query.message
    await reply_target.reply_html(get_text('welcome_existing', lang).format(dict=active_dict), reply_markup=keyboard)

async def handle_change_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    keyboard = get_dict_selection_inline_keyboard("set_default_dict")
    # Определяем, куда отвечать: в сообщение от команды или в сообщение с кнопкой
    reply_target = update.message or update.callback_query.message
    await reply_target.reply_text(get_text('available_dicts', lang), reply_markup=keyboard)

async def handle_change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    keyboard = get_lang_inline_keyboard()
    await update.message.reply_text(get_text('choose_lang_prompt', lang), reply_markup=keyboard)


# --- OTHER HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")
    
    if user.id not in user_language:
        await update.message.reply_html(
            TEXTS['ru']['welcome_new'].format(user=user.mention_html()),
            reply_markup=get_lang_inline_keyboard()
        )
        return

    lang = user_language.get(user.id)
    if user.id not in user_selected_dict:
        await handle_change_dict(update, context)
    else:
        await show_main_menu_and_welcome(update, context)

AWAITING_WORDS, AWAITING_DICT_CHOICE = range(2)

async def addword_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    await update.message.reply_text(get_text('addword_prompt', lang), reply_markup=ReplyKeyboardRemove())
    return AWAITING_WORDS

async def addword_receive_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['words_to_add'] = update.message.text.splitlines()
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    
    keyboard = get_dict_selection_inline_keyboard("addword_to_dict")
    await update.message.reply_text(get_text('addword_choose_dict', lang), reply_markup=keyboard)
    return AWAITING_DICT_CHOICE

async def dict_upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    await update.message.reply_text(get_text('upload_prompt', lang), reply_markup=ReplyKeyboardRemove())

async def dict_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    
    document = update.message.document
    if document and document.file_name.endswith('.txt'):
        file = await document.get_file()
        file_path = os.path.join(DICT_PATH, document.file_name)
        await file.download_to_drive(file_path)
        
        user_selected_dict[user_id] = document.file_name
        save_data(user_language, user_selected_dict)
        
        await update.message.reply_text(get_text('upload_success', lang).format(filename=document.file_name))
        await show_main_menu_and_welcome(update, context)
    else:
        await update.message.reply_text("Please send a .txt file.")


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except NetworkError as e:
        logger.error(f"Network error on query.answer(): {e}")
        return # Просто выходим, если не смогли ответить из-за сети
    except BadRequest as e:
        if "Query is too old" in str(e):
            logger.warning("Ignoring an old callback query.")
            return # Спокойно игнорируем старый запрос и выходим
        else:
            logger.error(f"BadRequest on query.answer(): {e}") # Логируем другие BadRequest ошибки
            return

    user_id = query.from_user.id
    data = query.data

    if data.startswith("set_lang:"):
        lang = data.split(":")[1]
        user_language[user_id] = lang
        save_data(user_language, user_selected_dict)
        logger.info(f"User {user_id} set language to {lang}")
        
        await query.edit_message_text(get_text('choose_dict_prompt', lang))
        # This is a bit of a trick: we need the `update` object for `handle_change_dict`, 
        # but `query` doesn't have `message`. We can use `query.message`.
        await handle_change_dict(update, context)
        return

    lang = user_language.get(user_id, 'en')

    if data.startswith("addword_to_dict:"):
        dict_name = data.split(":", 1)[1]
        words = context.user_data.get('words_to_add', [])
        if words:
            def append_words_to_file():
                with open(os.path.join(DICT_PATH, dict_name), 'a', encoding='utf-8') as f:
                    for word in words:
                        f.write(f"\n{word}")

            await asyncio.to_thread(append_words_to_file)

            await query.edit_message_text(get_text('addword_success', lang).format(dict_name=dict_name))
            context.user_data.clear()
            await show_main_menu_and_welcome(update, context)
        return ConversationHandler.END

    if data.startswith("set_default_dict:"):
        dict_name = data.split(":")[1]
        user_selected_dict[user_id] = dict_name
        save_data(user_language, user_selected_dict)
        logger.info(f"User {user_id} set default dict to {dict_name}")
        await query.edit_message_text(get_text('dict_changed', lang).format(dict=dict_name), parse_mode='HTML')
        await show_main_menu_and_welcome(update, context)
        return

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    await update.message.reply_text("Action canceled.", reply_markup=get_main_reply_keyboard(lang))
    return ConversationHandler.END

# --- MAIN FUNCTION TO RUN THE BOT ---
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # --- Handlers for Reply Keyboard buttons ---
    RANDOM_WORD_FILTER = filters.Text([TEXTS['en']['btn_random_word'], TEXTS['ru']['btn_random_word']])
    SETTINGS_FILTER = filters.Text([TEXTS['en']['btn_settings'], TEXTS['ru']['btn_settings']])
    CHANGE_DICT_FILTER = filters.Text([TEXTS['en']['btn_change_dict'], TEXTS['ru']['btn_change_dict']])
    CHANGE_LANG_FILTER = filters.Text([TEXTS['en']['btn_change_lang'], TEXTS['ru']['btn_change_lang']])
    BACK_TO_GAME_FILTER = filters.Text([TEXTS['en']['btn_back_to_game'], TEXTS['ru']['btn_back_to_game']])

    application.add_handler(MessageHandler(RANDOM_WORD_FILTER, handle_random_word))
    application.add_handler(MessageHandler(SETTINGS_FILTER, show_settings_menu))
    application.add_handler(MessageHandler(CHANGE_DICT_FILTER, handle_change_dict))
    application.add_handler(MessageHandler(CHANGE_LANG_FILTER, handle_change_lang))
    application.add_handler(MessageHandler(BACK_TO_GAME_FILTER, show_main_menu_and_welcome))
    
    # --- Other handlers ---
    addword_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addword", addword_start)],
        states={
            AWAITING_WORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, addword_receive_words)],
            AWAITING_DICT_CHOICE: [CallbackQueryHandler(button_callback_handler, pattern="^addword_to_dict:")],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )

    application.add_handler(addword_conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dict_upload", dict_upload_start))
    application.add_handler(MessageHandler(filters.Document.TXT, dict_upload_handler))
    
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    application.add_error_handler(error_handler)
    
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()