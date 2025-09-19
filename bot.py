import os
import logging
import random
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- НАСТРОЙКИ ---
# ВАЖНО: Вставьте сюда ваш токен, полученный от @BotFather
BOT_TOKEN = "***REMOVED***"
# Путь к папке со словарями
DICT_PATH = "dictionaries/"

# --- Внутренние переменные ---
# Словарь для хранения выбора пользователя {user_id: 'filename.txt'}
user_selected_dict = {}

# Настройка логирования для отладки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_available_dictionaries():
    """Сканирует папку DICT_PATH и возвращает список файлов .txt"""
    if not os.path.exists(DICT_PATH):
        os.makedirs(DICT_PATH)
    return [f for f in os.listdir(DICT_PATH) if f.endswith('.txt')]

def get_words_from_dict(filename: str, count: int = 0):
    """Читает слова из файла. Если count=0, возвращает все. Иначе - случайные."""
    try:
        with open(os.path.join(DICT_PATH, filename), 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        if count == 0:
            return words
        # Возвращаем count случайных слов без повторений
        return random.sample(words, min(count, len(words)))
    except FileNotFoundError:
        return []

# --- ГЕНЕРАТОРЫ КЛАВИАТУР ---

async def get_main_menu_keyboard():
    """Возвращает клавиатуру главного меню."""
    keyboard = [
        [InlineKeyboardButton("🎲 Случайное слово", callback_data="get_random_word")],
        [InlineKeyboardButton("🔢 Получить несколько", callback_data="show_get_multiple_menu")],
        [InlineKeyboardButton("⚙️ Сменить словарь", callback_data="change_dict_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_dict_selection_keyboard(action_prefix: str):
    """Возвращает клавиатуру для выбора словаря."""
    dictionaries = get_available_dictionaries()
    keyboard = [[InlineKeyboardButton(d.replace('.txt', ''), callback_data=f"{action_prefix}:{d}")] for d in dictionaries]
    return InlineKeyboardMarkup(keyboard)

async def get_multiple_words_keyboard():
    """Возвращает клавиатуру для выбора количества слов."""
    keyboard = [
        [
            InlineKeyboardButton("5", callback_data="get_multiple:5"),
            InlineKeyboardButton("10", callback_data="get_multiple:10"),
            InlineKeyboardButton("15", callback_data="get_multiple:15"),
        ],
        [InlineKeyboardButton("📜 Весь словарь", callback_data="get_multiple:all")],
        # Добавим кнопку для возврата в главное меню
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ОБРАБОТЧИКИ КОМАНД И КНОПОК ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")
    
    # Проверяем, выбрал ли пользователь словарь ранее
    if user.id not in user_selected_dict:
        await update.message.reply_html(
            f"👋 Привет, {user.mention_html()}!\n\n"
            "Похоже, ты здесь впервые. Пожалуйста, выбери словарь, который будем использовать по умолчанию:"
        )
        # Показываем меню выбора словаря
        keyboard = await get_dict_selection_keyboard("set_default_dict")
        await update.message.reply_text("Доступные словари:", reply_markup=keyboard)
    else:
        # Если пользователь уже есть, показываем главное меню
        active_dict = user_selected_dict[user.id]
        keyboard = await get_main_menu_keyboard()
        await update.message.reply_text(
            f"Твой активный словарь: <b>{active_dict}</b>\n\nВыбери действие:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик всех нажатий на inline-кнопки."""
    query = update.callback_query
    await query.answer()  # Обязательно, чтобы убрать "часики" на кнопке
    
    user_id = query.from_user.id
    data = query.data

    # --- Логика выбора словаря по умолчанию ---
    if data.startswith("set_default_dict:"):
        dict_name = data.split(":")[1]
        user_selected_dict[user_id] = dict_name
        logger.info(f"User {user_id} set default dict to {dict_name}")
        await query.edit_message_text(f"Отлично! Твой словарь по умолчанию: <b>{dict_name}</b>.", parse_mode='HTML')
        # Показываем главное меню после выбора
        keyboard = await get_main_menu_keyboard()
        await query.message.reply_text("Теперь можно начинать:", reply_markup=keyboard)
        return

    # Проверка, что словарь у пользователя вообще выбран
    if user_id not in user_selected_dict:
        await query.edit_message_text("Сначала нужно выбрать словарь! Пожалуйста, отправь команду /start")
        return

    active_dict = user_selected_dict[user_id]

    # --- Логика кнопок главного меню ---
    if data == "get_random_word":
        word = get_words_from_dict(active_dict, 1)
        if word:
            await query.edit_message_text(f"🎲 Слово: <b>{word[0]}</b>", parse_mode='HTML')
        else:
            await query.edit_message_text("В словаре нет слов или он пуст!")
        # Возвращаем главное меню, чтобы можно было играть дальше
        await query.message.reply_text("Что дальше?", reply_markup=await get_main_menu_keyboard())

    elif data == "show_get_multiple_menu":
        keyboard = await get_multiple_words_keyboard()
        await query.edit_message_text("Выбери, сколько слов ты хочешь получить:", reply_markup=keyboard)
        
    elif data == "change_dict_menu":
        keyboard = await get_dict_selection_keyboard("set_default_dict")
        await query.edit_message_text("Выбери новый словарь по умолчанию:", reply_markup=keyboard)
        
    elif data == "back_to_main_menu":
        keyboard = await get_main_menu_keyboard()
        await query.edit_message_text(
            f"Твой активный словарь: <b>{active_dict}</b>\n\nВыбери действие:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    # --- Логика получения нескольких слов ---
    elif data.startswith("get_multiple:"):
        param = data.split(":")[1]
        
        if param == 'all':
            words_to_get = 0 # 0 - значит все слова
        else:
            words_to_get = int(param)
        
        word_list = get_words_from_dict(active_dict, words_to_get)

        if not word_list:
            await query.edit_message_text("В словаре нет слов!")
            return

        # 🔥 Новая логика: если слов <= 10, отправляем текстом. Иначе - файлом.
        if len(word_list) <= 10:
            response_text = "Слова:\n" + "\n".join(f"• {w}" for w in word_list)
            await query.edit_message_text(response_text)
        else:
            # Создаем файл в памяти
            file_content = "\n".join(word_list).encode('utf-8')
            file_in_memory = BytesIO(file_content)
            # Отправляем файл
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file_in_memory,
                filename=f"words_from_{active_dict}"
            )
            # Убираем клавиатуру из предыдущего сообщения
            await query.edit_message_text("✅ Твой файл со словами готов:")

        # Возвращаем в главное меню
        await query.message.reply_text("Что дальше?", reply_markup=await get_main_menu_keyboard())


# --- ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ---
def main():
    """Запуск бота."""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    # Запускаем бота
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()