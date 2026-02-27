# --- TEXTS FOR LOCALIZATION ---
DEFAULT_LANG = 'ru'

TEXTS = {
    'en': {
        'welcome_new': """👋 Hi, {user}!

Looks like you're new here. Please choose your language:""",
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
        'btn_close': "❌ Close",
        'choose_lang_prompt': "Please choose your language:",
        'settings_menu_prompt': "⚙️ Settings Menu",
        'settings_info': "<b>Current Settings:</b>\n🌐 Language: {lang_name}\n📚 Dictionary: {dict_name}",
        'upload_prompt': "Send me a `.txt` file with words, each on a new line.",

        'upload_success': "✅ Dictionary `{filename}` uploaded and set as active.",
        'addword_prompt': "Send me the word(s) you want to add.",
        'addword_choose_dict': "Which dictionary to add the word(s) to?",
        'addword_success': "✅ Word(s) added to `{dict_name}`.",
        'admin_only': "⛔ This command is only for administrators.",
        'action_canceled': "Action canceled.",
        'invalid_file_type': "Please send a `.txt` file.",
    },
    'ru': {

        'welcome_new': """👋 Привет, {user}!

Похоже, ты здесь впервые. Пожалуйста, выбери язык:""",
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
        'btn_close': "❌ Закрыть",
        'choose_lang_prompt': "Пожалуйста, выберите язык:",
        'settings_menu_prompt': "⚙️ Меню настроек",
        'settings_info': "<b>Текущие настройки:</b>\n🌐 Язык: {lang_name}\n📚 Словарь: {dict_name}",
        'upload_prompt': "Отправьте мне файл `.txt` со словами, каждое на новой строке.",

        'upload_success': "✅ Словарь `{filename}` загружен и установлен как активный.",
        'addword_prompt': "Отправьте мне слово (или слова), которые нужно добавить.",
        'addword_choose_dict': "В какой словарь добавить слова?",
        'addword_success': "✅ Слова добавлены в словарь `{dict_name}`.",
        'admin_only': "⛔ Эта команда доступна только администраторам.",
        'action_canceled': "Действие отменено.",
        'invalid_file_type': "Пожалуйста, отправьте файл формата `.txt`.",
    }
}


def get_text(key: str, lang: str, default_lang: str = 'ru'):
    return TEXTS.get(lang, TEXTS.get(default_lang, TEXTS['en'])).get(key, f"<{key}>")
