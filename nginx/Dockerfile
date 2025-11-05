FROM nginx:latest

# Устанавливаем envsubst для подстановки переменных
RUN apt-get update && apt-get install -y gettext-base && \
    rm -rf /var/lib/apt/lists/*

# Создаем папки для статики
RUN mkdir -p /app/staticfiles /app/media

# Копируем шаблон конфигурации
COPY nginx.conf /etc/nginx/nginx.conf.template


EXPOSE 80 443

CMD sh -c "if [ \"$DOMAIN\" != \"_\" ]; then mkdir -p /var/www/certbot; fi && envsubst '\$DOMAIN' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"
