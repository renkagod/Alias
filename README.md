# Alias Bot для Telegram 🎲
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

Профессиональный бот для игры в "Alias". Переписан с упором на скорость (кэширование, асинхронность) и удобство развертывания.

---

## 🛠 Быстрый старт (Zero Config)

Всего 3 шага, чтобы бот заработал:

1.  **Клонируйте репозиторий**:
    ```bash
    git clone https://github.com/renkagod/Alias.git && cd Alias
    ```

2.  **Настройте `.env`**:
    ```bash
    cp .env.example .env
    # Впишите ваш BOT_TOKEN в .env
    ```

3.  **Запустите**:
    ```bash
    docker compose up -d --build
    ```

Бот сам подхватит встроенные словари из папки `dictionaries/` и создаст файл данных в папке `data/`.

---

## ⚙️ Настройки (.env)
*   `BOT_TOKEN` — Токен вашего бота.
*   `ADMIN_IDS` — ID администраторов (через запятую). Если пусто — доступ к командам `/addword` и `/dict_upload` есть у всех.
*   `DEFAULT_LANG` — Язык по умолчанию (`ru`).

---

## 📂 Структура файлов на сервере
*   `dictionaries/` — Здесь лежат встроенные и загруженные словари (.txt).
*   `data/` — Здесь бот хранит `user_data.json` (создается автоматически).

---

Автор: **renkagod** ([hakuworking@gmail.com](mailto:hakuworking@gmail.com))
