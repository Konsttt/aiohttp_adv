## Aiohttp + (postgresql + sqlalchemy + asyncpg).

### Что реализовано:

1. CRUD для таблицы пользователей Users
2. CRUD дял таблицы объявлений Adv
3. Запрос get - вывести всех пользователей
4. Запрос get - вывести все объявления
5. login - post запрос проверки соответствия пользователя и пароля
6. get запрос - вывод всех объявлений пользователя по его id
7. Валидация пароля и почты.
8. Попытка докерезировать. Но в результате поднимается только контейнер с postgres.
   <br>(Много времени потратил, и порты разные и т.д. Но крашится контейнер с приложением:
ошибка:<br>"OSError: Multiple exceptions: [Errno 111] Connect call failed ('127.0.0.1', 5432), [Errno 99] Cannot assign requested address")


### Запуск:
```shell
pip install -r requirements.txt
```

```shell
docker-compose up -d
```
<br>Далее, если не поднимется контейнер приложения, то запуск из PyCharm:
<br>server.py - RUN.
<br>В clients.py - раскомментировать нужный запрос - RUN