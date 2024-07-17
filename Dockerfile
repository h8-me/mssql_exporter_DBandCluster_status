# Используем базовый образ Python
FROM python:3.8-slim

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y curl gnupg && apt-get install -y unixodbc-dev && rm -rf /var/lib/apt/lists/*

# Установка ключа Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Добавление репозитория
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Обновление списка пакетов
RUN apt-get update

# Устанавливаем библиотеки Python
RUN pip install pymssql prometheus_client

# Копируем ваш Python-скрипт в контейнер
COPY exporterfull.py /usr/src/app/exporterfull.py

# Задаем рабочую директорию
WORKDIR /usr/src/app

# Запускаем Python-скрипт при старте контейнера
CMD ["python", "exporterfull.py"]
