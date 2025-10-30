# создаем контейнер для джанго-приложения на основе образа python 3.13-slim
FROM python:3.13-slim
# задаем корневую директорию для джанго-приложения
WORKDIR /app
# обновляем и устанавливаем нужные пакеты, создаем вирт.окружение в контейнере из requirements
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# копируем в контейнер все файлы проекта
COPY . .
# открываем в контейнере порт 8000 для работы с джанго-приложением
EXPOSE 8000
# собираем статические файлы, применяем миграции и заполняем БД из фикстур
CMD sh -c "python manage.py collectstatic --noinput && \
           python manage.py migrate && \
           python manage.py loaddata fixtures/users.json && \
           python manage.py loaddata fixtures/product_categories.json && \
           python manage.py loaddata fixtures/products.json && \
           python manage.py loaddata fixtures/publications.json && \
           python manage.py loaddata fixtures/publication_photos.json && \
           gunicorn config.wsgi:application --bind 0.0.0.0:8000"
