# Alias Bot для Telegram 🎲
🇷🇺 [Русский](#alias-bot-для-telegram) | 🇬🇧 [English](#alias-bot-for-telegram-en)

Простой и мощный бот для игры в "Alias" прямо в Telegram. Переписан для работы в Docker, обладает высокой скоростью работы и удобной настройкой.

---

## 🚀 Возможности

*   **🎲 Случайные слова:** Получение слов из активного словаря в один клик.
*   **🔗 Определения:** Каждое слово — это ссылка на Викисловарь для уточнения значения.
*   **⚙️ Настройки:** Удобное меню для смены словаря и языка интерфейса.
*   **🌍 Мультиязычность:** Полная поддержка русского и английского языков.
*   **✏️ Управление словарями (Админ):**
    *   Загрузка собственных `.txt` словарей через бота.
    *   Добавление новых слов прямо в чате.
*   **🐳 Docker:** Быстрый запуск и изоляция проекта.
*   **⚡ Оптимизация:** Кэширование словарей в памяти и асинхронный ввод-вывод.

## 🛠 Установка и запуск (Docker)

1.  **Клонируйте репозиторий**:
    ```bash
    git clone https://github.com/renkagod/Alias.git
    cd Alias
    ```

2.  **Настройте переменные окружения**:
    Скопируйте пример конфига и впишите ваш `BOT_TOKEN` в `.env`:
    ```bash
    cp .env.example .env
    ```

3.  **Запустите проект**:
    ```bash
    docker compose up -d --build
    ```

Бот автоматически подхватит словари из папки `dictionaries/` и создаст файл данных в папке `data/`.

## 🤖 Команды

*   `/start` — Запуск бота и выбор языка/словаря.
*   `/dict_upload` — Загрузка файла `.txt` со словами (для админов).
*   `/addword` — Добавление новых слов в словарь (для админов).
*   `/cancel` — Отмена текущего действия.

---

# Alias Bot for Telegram <a name="alias-bot-for-telegram-en"></a>
🇬🇧 [English](#alias-bot-for-telegram-en) | 🇷🇺 [Русский](#alias-bot-для-telegram)

A simple and powerful bot for playing "Alias" directly in Telegram. Rewritten for Docker, optimized for performance, and easy to configure.

## 🚀 Features

*   **🎲 Random Words:** Get words from the active dictionary with a single click.
*   **🔗 Definitions:** Each word is a link to Wiktionary for quick meaning lookup.
*   **⚙️ Settings:** Convenient menu to change dictionaries and interface language.
*   **🌍 Multilingual:** Full support for Russian and English.
*   **✏️ Dictionary Management (Admin):**
    *   Upload custom `.txt` dictionaries via the bot.
    *   Add new words directly in the chat.
*   **🐳 Docker:** Fast deployment and isolation.
*   **⚡ Performance:** Dictionary caching and asynchronous I/O.

## 🛠 Installation and Launch (Docker)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/renkagod/Alias.git
    cd Alias
    ```

2.  **Configure environment variables**:
    Copy the example config and put your `BOT_TOKEN` in `.env`:
    ```bash
    cp .env.example .env
    ```

3.  **Start the project**:
    ```bash
    docker compose up -d --build
    ```

The bot will automatically pick up dictionaries from the `dictionaries/` folder and create a data file in the `data/` folder.

## 🤖 Commands

*   `/start` — Start the bot and choose language/dictionary.
*   `/dict_upload` — Upload a `.txt` file with words (for admins).
*   `/addword` — Add new words to the dictionary (for admins).
*   `/cancel` — Cancel current action.
