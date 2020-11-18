# Проект по курсу "Программные средства для задач искусственного интеллекта"
Реализован упрощенный аналог https://telegra.ph/
1. Веб фрейморк: Flask
2. Для хранения данных используется Redis

Развёртывание с помощью `Docker Compose`:
```sh
$ git clone https://github.com/ugadiarov-la-phystech-edu/tlgrph.git
$ cd tlgrph
$ docker-compose up
```
По умолчанию доступ к веб-приложению осуществляется через порт хоста `15000` (настройка через `docker-compose.yml`).
