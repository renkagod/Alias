FROM python:3.10-slim

# Установка рабочей директории
WORKDIR /app

# Установка переменной для моментального вывода логов
ENV PYTHONUNBUFFERED=1

# Установка системных зависимостей (если понадобятся в будущем)
RUN apt-get update && apt-get install -y --no-install-recommends 
    build-essential 
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода бота
COPY . .

# Создание папки для данных и словарей (чтобы не было ошибок доступа)
RUN mkdir -p /data/dictionaries

# Запуск бота
CMD ["python", "main.py"]
