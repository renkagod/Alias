# Alias Bot для Telegram 🎲
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

## 🚀 Основные фичи
- **⚡ Оптимизация**: Кэширование, асинхронный ввод-вывод.
- **🐳 Docker**: Полная поддержка Docker Compose.
- **💾 Сохранение данных**: Все файлы хранятся в папке `./data`.

---

## 🛠 Запуск в Docker (по-умному)

1.  **Склонируйте репозиторий**:
    ```bash
    git clone https://github.com/renkagod/Alias.git && cd Alias
    ```

2.  **Настройте `.env`**:
    ```bash
    cp .env.example .env
    ```

3.  **Подготовьте папку со словарями**:
    ```bash
    mkdir -p data/dictionaries
    cp dictionaries/*.txt data/dictionaries/
    ```

4.  **Запустите проект**:
    ```bash
    docker compose up -d --build
    ```

---

## 📂 Структура данных (Хост-машина)
```text
Alias/
├── data/                # <-- ЗДЕСЬ ВСЕ ДАННЫЕ
│   ├── dictionaries/    # Ваши словари .txt
│   └── user_data.json   # Создается автоматически
└── .env                 # Настройки бота
```

---

## ⚙️ Переменные окружения (.env)
| Переменная | Описание |
| :--- | :--- |
| `BOT_TOKEN` | Токен от @BotFather |
| `ADMIN_IDS` | ID администраторов |

---

Автор: **renkagod** ([hakuworking@gmail.com](mailto:hakuworking@gmail.com))
