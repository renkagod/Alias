# Alias Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/renkagod/Alias/actions/workflows/ci.yml/badge.svg)](https://github.com/renkagod/Alias/actions/workflows/ci.yml)

Telegram-бот для игры в «Alias»: случайные слова из `.txt`‑словарей, ссылки на Викисловарь, RU/EN интерфейс, загрузка словарей и добавление слов (для админов).

## Особенности

- **Случайные слова** из выбранного словаря
- **Определения** — ссылка на Викисловарь
- **RU / EN** интерфейс
- **Админка** — загрузка `.txt` и `/addword` (только для `ADMIN_IDS`)
- **Docker** — Python 3.11, асинхронный I/O, кеш словарей в памяти

## Быстрый старт (Docker)

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/renkagod/Alias.git
   cd Alias
   ```

2. Настройте окружение:

   ```bash
   cp .env.example .env
   # BOT_TOKEN от @BotFather
   # ADMIN_IDS — ваш Telegram ID (через запятую для нескольких админов)
   ```

3. Запуск:

   ```bash
   docker compose up -d --build
   ```

   В комплекте три словаря Alias 2017 (Easy / Normal / Hard) и `example.txt`. Свои колоды — в `dictionaries/` или через `/dict_upload`.

## Конфигурация (`.env`)

| Переменная | Описание |
|------------|----------|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ADMIN_IDS` | ID администраторов через запятую. Пусто — админ-команды **отключены** |
| `DEFAULT_LANG` | `ru` или `en` для новых пользователей |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Команды

| Команда | Описание |
|---------|----------|
| `/start` | Язык, словарь, главное меню |
| `/dict_upload` | Загрузка `.txt` (только админ) |
| `/addword` | Добавить слова в словарь (только админ) |
| `/cancel` | Отмена текущего диалога |

## Структура

| Путь | Назначение |
|------|------------|
| `app/` | Логика бота |
| `dictionaries/` | Словари (см. [dictionaries/README.md](dictionaries/README.md)) |
| `data/` | Настройки пользователей (`user_data.json`, не в git) |

## Локальный запуск (без Docker)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Требуется **Python 3.11+**.

## Лицензия

[MIT](LICENSE) — Copyright (c) 2026 [renkagod](https://github.com/renkagod).
