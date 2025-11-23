# Varnitsa

Этот проект предоставляет собой сайт пивоваренного завода "Варница", рассказывает об истории и применяемых технологиях в производстве, а также о продукции.

## Описание
Проект реализует сайт, состоящий из 5 веб-страниц:
* Главная - краткое представление завода и его продукции.
* Завод "Варница" - рассказ об истории и технологиях, применяемых на производстве.
* Каталог - здесь представлен ассортимент продукции завода, есть возможность сортировать по видам (разливное пиво, фасованное пиво, безалкогольное пиво, квас и лимонады). Можно перейти в карточку каждого товара и узнать более полное описание и характеристики сорта.
* Блог - статьи о пиве и безалкогольных напитках, здесь можно будет размещать новости и анонсы выпуска новых сортов.
* Контакты - на странице представлена контактная информация: адрес завода, телефоны и электронная почта руководителя отдела сбыта. Также на этой странице есть ссылка на форму обратной связи - можно написать отзыв или обращение прямо на сайте, прикрепить файлы и отправить сообщение. Эти сообщения будут распределяться в зависимости от темы и поступать в качестве писем на email ответственным за различные направления работы: сбыт, снабжение, качество продукции.

## Технологии
* Django - веб-фреймворк

* PostgreSQL - база данных

* Redis - кеширование

* HTML, CSS, JS - шаблонизация

* unittest - тестирование

* Docker - контейнеризация

* Git, CI/CD - система контроля версий, деплой на сервер

## Предварительные требования
- Docker Desktop (для Windows/Mac) или Docker Engine + Docker Compose (для Linux)

- Git, GitHub.
## Запуск сервера локально
* Создайте папку для приложения и сохраните в нее проект (на странице проекта на GitHub https://github.com/OksanaNiklashkova/Varnitsa нажмите зеленую кнопку <> Code и выберите Download ZIP, распакуйте архив).
* Создайте в этой папке .env файл с переменными по образцу из файла env.sample.
Эти переменные заполните так:

- DOMAIN=localhost
- WEB_IMAGE=varnitsa-web-local
- NGINX_IMAGE=varnitsa-nginx-local
- SECRET_KEY=django-insecure-rrr-rrrrrrrrrrrrrr-rrrrrrrrrrrrr-rrrrrrrrrrr-0-rrr
- DEBUG=False
- POSTGRES_DB=произвольно
- POSTGRES_USER=произвольно
- POSTGRES_PASSWORD=произвольно
- POSTGRES_HOST=db
- POSTGRES_PORT=5432

Настройки почтового сервера можно не заполнять, если они не заданы, не будут отправляться письма с обращениями посетителей, но в тестовом режиме это не обязательно.
* Установите Docker Desktop https://docs.docker.com/desktop/setup/install/windows-install/ и запустите его.
* Проверьте, что Docker доступен в командной строке:
```
cd <путь до вашей папки с проектом>
docker compose --version
```
* Запустите сборку контейнеров `docker compose up --build`
* Проверьте, что все контейнеры работают `docker compose ps`
Вы должны увидеть список из контейнеров: varnitsa_web, varnitsa_db, varnitsa_redis, nginx в статусе Up.

* Для начального заполнения базы данных нужно воспользоваться фикстурами, имеющимися в папке fixtures:
~~~
docker compose run --rm varnitsa_web python manage.py loaddata fixtures/users.json
docker compose run --rm varnitsa_web python manage.py loaddata fixtures/product_categories.json
docker compose run --rm varnitsa_web python manage.py loaddata fixtures/products.json
docker compose run --rm varnitsa_web python manage.py loaddata fixtures/publications.json
docker compose run --rm varnitsa_web python manage.py loaddata fixtures/publication_photos.json
~~~
Создайте superuser, если хотите авторизоваться в приложении и иметь доступ к CRUD продуктов и статей.

После успешного запуска перейдите по адресу: http://localhost:8000/

Не авторизованный пользователь может, подтвердив, что ему более 18 лет, просматривать все страницы сайта и отправлять сообщения на странице "Контакты" -> Форма обращения.
* В рамках учебного проекта сервер развернут на базе CloudPub по адресу: https://weekly-manageable-tarpon.cloudpub.ru/


## Запуск сервера с помощью CI/CD на виртуальной машине
#### Подготовка сервера.
Создайте виртуальную машину, подключитесь к ней.

```
# Подключение к серверу
ssh username@server_ip

# Установка Docker
sudo apt update && sudo apt install docker.io -y

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
# Перезапустите сессию SSH
```
#### Настройка окружения

Склонируйте репозиторий проекта 
```
git clone https://github.com/OksanaNiklashkova/Varnitsa.git
```
Разместите репозиторий с проектом на GitHub.

В личном кабинете на GitHub в репозитории с проектом в GitHub Secrets добавьте:

* DOMAIN - если сайт разворачивается с доменным именем, в противном случае будет подставлено значение "_" и будет использован протокол http.

* CERTBOT_EMAIL - почта для запросов на получение SSL-сертификатов

* GHCR_TOKEN - токен GitHub Container Registry с правами `read:packages`, `write:packages`

* SSH_KEY - приватный SSH ключ для доступа к серверу, указанный при создании виртуальной машины

* SSH_USER - пользователь сервера, указанный при создании виртуальной машины (например, user)

* SERVER_IP - IP адрес сервера

* DJANGO_SECRET_KEY - секретный ключ от Джанго приложения.

* POSTGRES_DB - название базы данных, например, varnitsa_db

* POSTGRES_USER - пользователь базы данных, по умолчанию - postgres
          
* POSTGRES_PASSWORD - пароль от базы данных, произвольный
          
* POSTGRES_HOST - по умолчанию - db
          
* EMAIL_BACKEND - например, django.core.mail.backends.smtp.EmailBackend

* EMAIL_HOST - например, smtp.yandex.ru

* EMAIL_POR - по умолчанию 465

* EMAIL_USE_TLS и EMAIL_USE_SSL - со значениями True или False в зависимости от выбранного smtp-сервера

* EMAIL_HOST_USER и EMAIL_HOST_PASSWORD - адрес для отправки сообщений о поступивших обращениях на сайте и пароль от smtp-сервиса.

Сделайте в репозитории push или pull-request, это автоматически запустит тестирование, создание контейнера и деплой на ваш сервер.

#### Проверка работоспособности
Перейдите по IP-адресу вашего сервера. 

Современные браузеры оценивают http-протокол как менее безопасный, по сравнению с https.
Если браузер выбрасывает сообщение о потенциальной небезопасности, нажмите "Посмотреть детали" => "Все равно перейти". 

## Тестирование

В рамках проекта реализовано тестирование всех эндпойнтов с помощью unittest. 

## Использование

Для начального заполнения базы данных нужно воспользоваться фикстурами, имеющимися в папке fixtures:
~~~
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/product_categories.json
python manage.py loaddata fixtures/products.json
python manage.py loaddata fixtures/publications.json
python manage.py loaddata fixtures/publication_photos.json
~~~

## Зависимости

Проект использует следующие зависимости:

*   Python 3.13
*   Poetry (для управления зависимостями)
*   django==5.2.7
*   flake8==7.3.0
*   gunicorn==23.0.0
*   pillow==11.3.0
*   psycopg2-binary==2.9.10
*   python-dotenv==1.1.1
*   redis==6.4.0
*   whitenoise==6.11.0

## Лицензия

Этот проект лицензирован по [лицензии MIT](LICENSE).