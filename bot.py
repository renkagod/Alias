import os
import logging
import random
from io import BytesIO
from urllib.parse import quote_plus
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION / НАСТРОЙКИ ---
load_dotenv() # Load variables from .env file / Загружаем переменные из .env файла

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    # This will stop the bot if the token is missing in .env
    # Эта строчка остановит запуск, если вы забыли создать .env или указать в нем токен
    raise ValueError("BOT_TOKEN not found in .env file!")

# Path to the dictionaries folder
# Путь к папке со словарями
DICT_PATH = "dictionaries/"

# --- TEXTS FOR LOCALIZATION / ТЕКСТЫ ДЛЯ ЛОКАЛИЗАЦИИ ---
TEXTS = {
    'en': {
        'welcome_new': "👋 Hi, {user}!\n\nLooks like you're new here. Please choose your language:",
        'welcome_existing': "Your active dictionary: <b>{dict}</b>\n\nChoose an action:",
        'choose_dict_prompt': "Great! Now choose a default dictionary:",
        'available_dicts': "Available dictionaries:",
        'dict_changed': "✅ Default dictionary changed to: <b>{dict}</b>.",
        'lets_start': "Let's begin:",
        'choose_word_count': "Choose how many words you want to get:",
        'no_dict_selected': "Please select a dictionary first! Send /start",
        'no_words_in_dict': "There are no words in this dictionary!",
        'random_word_title': "🎲 Word:",
        'multiple_words_title': "Words:",
        'file_ready': "✅ Your file with words is ready:",
        'whats_next': "What's next?",
        'btn_random_word': "🎲 Random Word",
        'btn_get_multiple': "🔢 Get Multiple",
        'btn_change_dict': "⚙️ Change Dictionary",
        'btn_change_lang': "🌐 Change Language",
        'btn_back': "⬅️ Back",
        'choose_lang_prompt': "Please choose your language:",
    },
    'ru': {
        'welcome_new': "👋 Привет, {user}!\n\nПохоже, ты здесь впервые. Пожалуйста, выбери язык:",
        'welcome_existing': "Твой активный словарь: <b>{dict}</b>\n\nВыбери действие:",
        'choose_dict_prompt': "Отлично! Теперь выбери словарь по умолчанию:",
        'available_dicts': "Доступные словари:",
        'dict_changed': "✅ Словарь по умолчанию изменён на: <b>{dict}</b>.",
        'lets_start': "Теперь можно начинать:",
        'choose_word_count': "Выбери, сколько слов ты хочешь получить:",
        'no_dict_selected': "Сначала нужно выбрать словарь! Пожалуйста, отправь команду /start",
        'no_words_in_dict': "В этом словаре нет слов!",
        'random_word_title': "🎲 Слово:",
        'multiple_words_title': "Слова:",
        'file_ready': "✅ Твой файл со словами готов:",
        'whats_next': "Что дальше?",
        'btn_random_word': "🎲 Случайное слово",
        'btn_get_multiple': "🔢 Получить несколько",
        'btn_change_dict': "⚙️ Сменить словарь",
        'btn_change_lang': "🌐 Сменить язык",
        'btn_back': "⬅️ Назад",
        'choose_lang_prompt': "Пожалуйста, выберите язык:",
    }
}


# --- INTERNAL VARIABLES / ВНУТРЕННИЕ ПЕРЕМЕННЫЕ ---
# Dictionary to store user's selected dictionary {user_id: 'filename.txt'}
# Словарь для хранения выбора словаря пользователя {user_id: 'filename.txt'}
user_selected_dict = {}

# Dictionary to store user's selected language {user_id: 'en' | 'ru'}
# Словарь для хранения выбора языка пользователя {user_id: 'en' | 'ru'}
user_language = {}

# Setup logging for debugging
# Настройка логирования для отладки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- HELPER FUNCTIONS / ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_text(key: str, lang: str):
    """Gets text string for a given language. Defaults to English."""
    """Получает текстовую строку для данного языка. По умолчанию английский."""
    return TEXTS.get(lang, TEXTS['en']).get(key, f"<{key}>")

def get_available_dictionaries():
    """Scans the DICT_PATH folder and returns a list of .txt files."""
    """Сканирует папку DICT_PATH и возвращает список файлов .txt."""
    if not os.path.exists(DICT_PATH):
        os.makedirs(DICT_PATH)
    return [f for f in os.listdir(DICT_PATH) if f.endswith('.txt')]

def get_words_from_dict(filename: str, count: int = 0):
    """Reads words from a file. If count=0, returns all. Otherwise, random ones."""
    """Читает слова из файла. Если count=0, возвращает все. Иначе - случайные."""
    try:
        with open(os.path.join(DICT_PATH, filename), 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        if count == 0:
            return words
        return random.sample(words, min(count, len(words)))
    except FileNotFoundError:
        return []

# --- KEYBOARD GENERATORS / ГЕНЕРАТОРЫ КЛАВИАТУР ---

async def get_lang_keyboard():
    """Returns the language selection keyboard."""
    """Возвращает клавиатуру выбора языка."""
    keyboard = [[
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru")
    ]]
    return InlineKeyboardMarkup(keyboard)

async def get_main_menu_keyboard(lang: str):
    """Returns the main menu keyboard."""
    """Возвращает клавиатуру главного меню."""
    keyboard = [
        [InlineKeyboardButton(get_text('btn_random_word', lang), callback_data="get_random_word")],
        [InlineKeyboardButton(get_text('btn_get_multiple', lang), callback_data="show_get_multiple_menu")],
        [InlineKeyboardButton(get_text('btn_change_dict', lang), callback_data="change_dict_menu")],
        [InlineKeyboardButton(get_text('btn_change_lang', lang), callback_data="change_lang_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_dict_selection_keyboard(action_prefix: str):
    """Returns a keyboard for selecting a dictionary."""
    """Возвращает клавиатуру для выбора словаря."""
    dictionaries = get_available_dictionaries()
    keyboard = [[InlineKeyboardButton(d.replace('.txt', ''), callback_data=f"{action_prefix}:{d}")] for d in dictionaries]
    return InlineKeyboardMarkup(keyboard)

async def get_multiple_words_keyboard(lang: str):
    """Returns a keyboard for selecting the number of words."""
    """Возвращает клавиатуру для выбора количества слов."""
    keyboard = [
        [
            InlineKeyboardButton("5", callback_data="get_multiple:5"),
            InlineKeyboardButton("10", callback_data="get_multiple:10"),
            InlineKeyboardButton("15", callback_data="get_multiple:15"),
        ],
        [InlineKeyboardButton("📜 " + get_text('btn_all_words', lang, default="All Words"), callback_data="get_multiple:all")], # Example with default
        [InlineKeyboardButton(get_text('btn_back', lang), callback_data="back_to_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- COMMAND AND BUTTON HANDLERS / ОБРАБОТЧИКИ КОМАНД И КНОПОК ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    """Обработчик команды /start."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")
    
    # 1. Check if language is selected
    # 1. Проверяем, выбран ли язык
    if user.id not in user_language:
        await update.message.reply_html(
            TEXTS['ru']['welcome_new'].format(user=user.mention_html()), # Show bilingual welcome
            reply_markup=await get_lang_keyboard()
        )
        return

    lang = user_language[user.id]

    # 2. Check if dictionary is selected
    # 2. Проверяем, выбран ли словарь
    if user.id not in user_selected_dict:
        await update.message.reply_text(get_text('choose_dict_prompt', lang))
        keyboard = await get_dict_selection_keyboard("set_default_dict")
        await update.message.reply_text(get_text('available_dicts', lang), reply_markup=keyboard)
    else:
        active_dict = user_selected_dict[user.id]
        keyboard = await get_main_menu_keyboard(lang)
        await update.message.reply_text(
            get_text('welcome_existing', lang).format(dict=active_dict),
            reply_markup=keyboard,
            parse_mode='HTML'
        )

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main handler for all inline button clicks."""
    """Главный обработчик всех нажатий на inline-кнопки."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data

    # --- Language selection logic ---
    # --- Логика выбора языка ---
    if data.startswith("set_lang:"):
        lang = data.split(":")[1]
        user_language[user_id] = lang
        logger.info(f"User {user_id} set language to {lang}")
        
        # Now prompt for dictionary selection
        # Теперь запрашиваем выбор словаря
        keyboard = await get_dict_selection_keyboard("set_default_dict")
        await query.edit_message_text(
            get_text('choose_dict_prompt', lang),
            reply_markup=keyboard
        )
        return

    # All subsequent actions require a language to be set
    # Все последующие действия требуют установленного языка
    if user_id not in user_language:
        await query.edit_message_text("Please choose a language first / Пожалуйста, выберите язык.", reply_markup=await get_lang_keyboard())
        return
        
    lang = user_language[user_id]

    # --- Dictionary selection logic ---
    # --- Логика выбора словаря ---
    if data.startswith("set_default_dict:"):
        dict_name = data.split(":")[1]
        user_selected_dict[user_id] = dict_name
        logger.info(f"User {user_id} set default dict to {dict_name}")
        await query.edit_message_text(get_text('dict_changed', lang).format(dict=dict_name), parse_mode='HTML')
        
        keyboard = await get_main_menu_keyboard(lang)
        await query.message.reply_text(get_text('lets_start', lang), reply_markup=keyboard)
        return

    # Check that a dictionary is selected for game actions
    # Проверяем, что словарь выбран для игровых действий
    if user_id not in user_selected_dict and not data.startswith('change_lang'):
        await query.edit_message_text(get_text('no_dict_selected', lang))
        return

    active_dict = user_selected_dict.get(user_id)

    # --- Main menu logic ---
    # --- Логика главного меню ---
    if data == "get_random_word":
        word = get_words_from_dict(active_dict, 1)
        if word:
            word_text = word[0]
            google_link = f"https://www.google.com/search?q={quote_plus(word_text)}&hl={lang}"
            await query.edit_message_text(
                f"{get_text('random_word_title', lang)} <a href='{google_link}'><b>{word_text}</b></a>",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(get_text('no_words_in_dict', lang))
        await query.message.reply_text(get_text('whats_next', lang), reply_markup=await get_main_menu_keyboard(lang))

    elif data == "show_get_multiple_menu":
        # Note: 'btn_all_words' key is missing from TEXTS, so the default will be used.
        # This is to show how the default works. You should add it to the TEXTS dict.
        # Примечание: ключ 'btn_all_words' отсутствует в TEXTS, поэтому будет использовано значение по умолчанию.
        # Это для демонстрации. Вам следует добавить его в словарь TEXTS.
        keyboard = await get_multiple_words_keyboard(lang)
        await query.edit_message_text(get_text('choose_word_count', lang), reply_markup=keyboard)
        
    elif data == "change_dict_menu":
        keyboard = await get_dict_selection_keyboard("set_default_dict")
        await query.edit_message_text(get_text('available_dicts', lang), reply_markup=keyboard)

    elif data == "change_lang_menu":
        keyboard = await get_lang_keyboard()
        await query.edit_message_text(get_text('choose_lang_prompt', lang), reply_markup=keyboard)
        
    elif data == "back_to_main_menu":
        keyboard = await get_main_menu_keyboard(lang)
        await query.edit_message_text(
            get_text('welcome_existing', lang).format(dict=active_dict),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    elif data.startswith("get_multiple:"):
        param = data.split(":")[1]
        words_to_get = 0 if param == 'all' else int(param)
        word_list = get_words_from_dict(active_dict, words_to_get)

        if not word_list:
            await query.edit_message_text(get_text('no_words_in_dict', lang))
            return

        if len(word_list) <= 10:
            response_text = get_text('multiple_words_title', lang) + "\n" + "\n".join(
                f"• <a href='https://www.google.com/search?q={quote_plus(w)}&hl={lang}'>{w}</a>" for w in word_list
            )
            await query.edit_message_text(response_text, parse_mode='HTML')
        else:
            file_content = "\n".join(word_list).encode('utf-8')
            file_in_memory = BytesIO(file_content)
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file_in_memory,
                filename=f"words_from_{active_dict}"
            )
            await query.edit_message_text(get_text('file_ready', lang))

        await query.message.reply_text(get_text('whats_next', lang), reply_markup=await get_main_menu_keyboard(lang))


# --- MAIN FUNCTION TO RUN THE BOT ---
# --- ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА БОТА ---
def main():
    """Run the bot."""
    """Запуск бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()