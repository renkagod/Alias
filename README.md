# Alias Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/renkagod/Alias/actions/workflows/ci.yml/badge.svg)](https://github.com/renkagod/Alias/actions/workflows/ci.yml)

Telegram-бот для игры в «Alias»: случайные слова из `.txt`-словарей, ссылки на определения в Викисловаре, RU/EN интерфейс, загрузка словарей и добавление слов для администраторов.

## Особенности

- Случайные слова из выбранного словаря, кеш словарей в памяти
- Ссылка на определение слова в Викисловаре (ru/en)
- RU / EN интерфейс
- Админка — загрузка `.txt` и `/addword` (только для `ADMIN_IDS`)
- Три готовых словаря Alias 2017 (Easy / Normal / Hard) и пример для своего

## Быстрый старт

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/renkagod/Alias.git
   cd Alias
   ```

2. Настройте окружение:

   ```bash
   cp .env.example .env
   # BOT_TOKEN — токен от @BotFather
   # ADMIN_IDS — ваш Telegram ID (через запятую для нескольких админов)
   ```

3. Запуск:

   ```bash
   docker compose up -d --build
   ```

В комплекте три словаря Alias 2017 (Easy / Normal / Hard) и `example.txt`. Свои колоды — в `dictionaries/` или через `/dict_upload`.

## Конфигурация (`.env`)

| Переменная | Обязательна | Описание |
|------------|--------------|----------|
| `BOT_TOKEN` | да | Токен бота от @BotFather |
| `ADMIN_IDS` | нет | ID администраторов через запятую. Пусто — админ-команды отключены |
| `DEFAULT_LANG` | нет | `ru` или `en` для новых пользователей (по умолчанию `ru`) |
| `LOG_LEVEL` | нет | `DEBUG`, `INFO`, `WARNING`, `ERROR` (по умолчанию `INFO`) |

## Команды

| Команда | Описание |
|---------|----------|
| `/start` | Язык, словарь, главное меню |
| `/dict_upload` | Загрузка `.txt` (только админ) |
| `/addword` | Добавить слова в словарь (только админ) |
| `/cancel` | Отмена текущего диалога |

## Docker

`Dockerfile` собирает образ на `python:3.11-slim`. `docker-compose.yml` монтирует `./dictionaries` и `./data` как volumes и ограничивает контейнер `alias-bot` до 256 MB / 0.5 CPU (резерв — 64 MB / 0.1 CPU).

```bash
docker compose up -d --build   # запуск
docker compose logs -f         # логи
docker compose down            # остановка
```

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

Требуется Python 3.11+.

## Лицензия

[MIT](LICENSE) — Copyright (c) 2026 [renkagod](https://github.com/renkagod).
