#!/bin/sh

# Подставляем переменные окружения в nginx.conf
envsubst '$DOMAIN' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Проверяем синтаксис
nginx -t

# Запускаем nginx
exec nginx -g "daemon off;"