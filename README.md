# Alias Bot для Telegram

Простой и удобный бот для игры в "Alias" с друзьями прямо в Telegram.

## 🚀 Возможности

  * **🎲 Случайные слова:** Получение слов из активного словаря по нажатию одной кнопки.
  * **🔗 Точные определения:** Каждое слово — это кликабельная ссылка на **Викисловарь** для быстрого уточнения значения.
  * **⚙️ Гибкие настройки:** Удобное меню для смены активного словаря и языка интерфейса.
  * **🌍 Два языка:** Бот полностью поддерживает русский и английский языки.
  * **✏️ Управление словарями:**
      * Загружайте собственные словари командой `/dict_upload`.
      * Добавляйте новые слова в любой словарь командой `/addword`.
  * **💾 Сохранение сессии:** Бот помнит ваш выбранный язык и словарь даже после перезапуска.

## 🔧 Установка и запуск

1.  **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/renkagod/Alias.git
    cd Alias
    ```

2.  **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Настройте переменные окружения:**

      * Создайте файл `.env` в корневой папке.
      * Добавьте в него ваш токен: `BOT_TOKEN="ВАШ_ТОКЕН_ОТ_BOTFATHER"`

4.  **Запустите бота:**

    ```bash
    python bot.py
    ```

## 🤖 Команды

  * `/start` - Запустить бота и пройти первоначальную настройку.
  * `/dict_upload` - Загрузить свой файл `.txt` со словами.
  * `/addword` - Добавить одно или несколько новых слов в существующий словарь.

-----

-----

# Alias Bot for Telegram

A simple and convenient bot for playing "Alias" with friends directly in Telegram.

## 🚀 Features

  * **🎲 Random Words:** Get words from the active dictionary with a single button press.
  * **🔗 Precise Definitions:** Each word is a clickable link to **Wiktionary** for a quick and accurate definition.
  * **⚙️ Flexible Settings:** A convenient menu to change the active dictionary and interface language.
  * **🌍 Bilingual:** The bot fully supports Russian and English.
  * **✏️ Dictionary Management:**
      * Upload your own dictionaries with the `/dict_upload` command.
      * Add new words to any dictionary with the `/addword` command.
  * **💾 Session Persistence:** The bot remembers your chosen language and dictionary even after a restart.

## 🔧 Installation and Launch

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/renkagod/Alias.git
    cd Alias
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**

      * Create a `.env` file in the root folder.
      * Add your token to it: `BOT_TOKEN="YOUR_TOKEN_FROM_BOTFATHER"`

4.  **Start the bot:**

    ```bash
    python bot.py
    ```

## 🤖 Commands

  * `/start` - Start the bot and complete the initial setup.
  * `/dict_upload` - Upload your own `.txt` file with words.
  * `/addword` - Add one or more new words to an existing dictionary.