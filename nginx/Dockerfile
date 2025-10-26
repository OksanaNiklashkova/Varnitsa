FROM nginx:latest

# Устанавливаем envsubst для подстановки переменных
RUN apt-get update && apt-get install -y gettext-base && \
    rm -rf /var/lib/apt/lists/*

# Создаем папки для статики
RUN mkdir -p /app/staticfiles /app/media

# Копируем шаблон конфигурации
COPY nginx.conf /etc/nginx/nginx.conf.template

# Копируем скрипт запуска
COPY start-nginx.sh /start-nginx.sh
RUN chmod +x /start-nginx.sh
EXPOSE 80 443

CMD ["/start-nginx.sh"]
