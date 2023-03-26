import json
from datetime import datetime

from aiohttp import web
from model import engine, Base, Session, User, Adv
from bcrypt import hashpw, gensalt, checkpw  # ф-ции для хеширования, для соли, для проверки пароля
from sqlalchemy.exc import IntegrityError  # делаем исключения на дублирование пользователей
from sqlalchemy.future import select  # похоже на корутин. С помощью этой штуки можно формировать запросы селекта
from validate import post_validate, patch_validate

app = web.Application()


# Специальный обработчик. До yield выполняются команды до старта сервера. После завершения работы сервера,
# выполняется, то что после yield
async def app_context(app):
    # print('Старт')
    # Запускаем первую миграцию
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print('Выход')


# Специальная функция обертка, автоматизирует открытие и закрытие сессии. Напоминает декоратор.
# В handler передаем нашу функцию, которую оборачиваем.
@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session  # К объекту реквеста прикрепляем сессию
        response = await handler(request)
        return response


# У app есть список middlewares и туда мы добавляем свой session_middleware
app.middlewares.append(session_middleware)  # обёртка открытия сессии
app.cleanup_ctx.append(app_context)  # обёртка для старта сервера


# Просто функция проверки пароля (без логики)
async def login(request: web.Request):  # Обычный веб.реквест на вход
    json_data = await request.json()  # Из реквеста получаем json, собственно в котором логин и пароль из запроса
    # Подключаемся к БД.
    # селект для асинхронной алхимии. Менее удобен чем для синхронной обычной алхимии
    query = select(User).where(User.email == json_data['email'])  # Создаем квери
    result = await request['session'].execute(query)  # Ищем из асинхронной сессии
    user = result.scalar()  # Получаем результат

    # Если юзера нашли, то проверяем у него пароль
    if user:
        # Первый аргумент пароль из запроса, второй аргумент пароль из БД для данного юзера
        # Сравниваем специальной функцией checkpw()
        is_password_correct = checkpw(json_data['password'].encode(), user.password.encode())
        if is_password_correct:
            return web.json_response({'status': 'success'})

    raise web.HTTPUnauthorized(
        text=json.dumps({'error': 'user or password is incorrect'}),
        content_type='application/json'
    )


# Вспомогательная функция для get User
async def get_user(user_id: int, session: Session):
    user = await session.get(User, user_id)

    if user is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'user not found'}),
                               content_type='application/json')
    return user


# Функция для запроса по всем пользователям с помощью стримминга.
async def get_users(request: web.Request):
    response = web.StreamResponse()
    await response.prepare(request)
    query = select(User)
    users = await request['session'].execute(query)
    for user in users.scalars():
        await response.write(
            json.dumps({'id': user.id,
                        'email': user.email,
                        'registration_time': int(user.registration_time.timestamp())}).encode()
        )
    return response


# Вьюха для таблицы User
class UserView(web.View):

    async def get(self):
        user = await get_user(int(self.request.match_info['user_id']), self.request['session'])
        return web.json_response({
            'id': user.id,
            'email': user.email,
            # 'creation_time': int(user.creation_time.timestamp())  # в UTC
            'registration_time':
                datetime.utcfromtimestamp(int(user.registration_time.timestamp())).strftime('%Y-%m-%d %H:%M:%S')
        })

    async def post(self):
        json_data = await self.request.json()
        json_data = await post_validate(json_data)  # Валидация email и пароля
        json_data['password'] = hashpw(json_data['password'].encode(), salt=gensalt()).decode()
        user = User(**json_data)
        self.request['session'].add(user)
        try:
            await self.request['session'].commit()
        except IntegrityError as er:
            raise web.HTTPConflict(
                text=json.dumps({"error": "user already exists"}),
                content_type='application/json'
            )
        return web.json_response({'id': user.id, 'email': user.email, 'password': user.password})

    async def patch(self):
        user = await get_user(int(self.request.match_info['user_id']), self.request['session'])
        json_data = await self.request.json()
        json_data = await patch_validate(json_data)  # Валидация email и пароля
        # Шифруем пароль, только если он есть в патч запросе.
        if json_data.get('password'):
            json_data['password'] = hashpw(json_data['password'].encode(), salt=gensalt()).decode()
        for field, value in json_data.items():
            setattr(user, field, value)
            self.request['session'].add(user)
            await self.request['session'].commit()
        return web.json_response({'status': 'success'})

    async def delete(self):
        user = await get_user(int(self.request.match_info['user_id']), self.request['session'])
        await self.request['session'].delete(user)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})


# Вспомогательная функция для get Adv
async def get_adv(adv_id: int, session: Session):
    adv = await session.get(Adv, adv_id)

    if adv is None:
        raise web.HTTPNotFound(text=json.dumps({'status': 'error', 'message': 'This advertisement not found'}),
                               content_type='application/json')
    return adv

###################
# Функция для запроса по всем объявлениям с помощью стримминга.
async def get_advs(request: web.Request):
    response = web.StreamResponse()
    await response.prepare(request)
    query = select(Adv)
    advs = await request['session'].execute(query)
    for adv in advs.scalars():
        await response.write(
            json.dumps({'id': adv.id,
                        'title': adv.title,
                        'message': adv.message,
                        'owner': adv.owner,
                        'creation_time': int(adv.creation_time.timestamp())}).encode()
        )
    return response


# Функция для запроса по всем объявлениям конкретного пользователя с помощью стримминга.
async def get_owner_advs(request: web.Request):
    owner_id = int(request.match_info['owner_id'])
    response = web.StreamResponse()
    await response.prepare(request)
    query = select(Adv).filter(Adv.owner_id == owner_id)
    advs = await request['session'].execute(query)
    for adv in advs.scalars():
        await response.write(
            json.dumps({'id': adv.id,
                        'title': adv.title,
                        'message': adv.message,
                        'owner': adv.owner,
                        'creation_time': int(adv.creation_time.timestamp())}).encode()
        )
    return response


# Вьюха для таблицы Adv
class AdvView(web.View):

    async def get(self):
        adv = await get_adv(int(self.request.match_info['adv_id']), self.request['session'])
        return web.json_response({
            'id': adv.id,
            'title': adv.title,
            'message': adv.message,
            'owner': adv.owner,
            'owner_id': adv.owner_id,
            'creation_time': datetime.utcfromtimestamp(int(adv.creation_time.timestamp())).strftime('%Y-%m-%d %H:%M:%S')
        })

    async def post(self):
        json_data = await self.request.json()
        adv = Adv(**json_data)
        self.request['session'].add(adv)
        try:
            await self.request['session'].commit()
        except IntegrityError as er:
            raise web.HTTPConflict(
                text=json.dumps({"error": "This advertisement already exists"}),
                content_type='application/json'
            )
        return web.json_response({'id': adv.id, 'title': adv.title, 'owner': adv.owner})

    async def patch(self):
        adv = await get_adv(int(self.request.match_info['adv_id']), self.request['session'])
        json_data = await self.request.json()
        for field, value in json_data.items():
            setattr(adv, field, value)
            self.request['session'].add(adv)
            await self.request['session'].commit()
        return web.json_response({'status': 'success'})

    async def delete(self):
        adv = await get_adv(int(self.request.match_info['adv_id']), self.request['session'])
        await self.request['session'].delete(adv)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})


# вьюху привязываем к url-y
# для этого есть метод add_routes, которому списком можно передавать url-ы
# роуты - это экземпляры класса web.get, web.post, web.patch и т.д.
app.add_routes([
    # роуты по пользователям user
    web.get('/user/{user_id:\d+}', UserView),
    web.post('/user', UserView),
    web.patch('/user/{user_id:\d+}', UserView),
    web.delete('/user/{user_id:\d+}', UserView),
    # Метод post для логина. Т.е. мы просто постом передаём json с данными.
    # Да с get логин тоже работает проверял, без разницы.
    web.post('/login', login),
    # Запрос по всем пользователям. С помощью стриминг.
    web.get('/users', get_users),

    # роуты для объявлений adv
    web.get('/adv/{adv_id:\d+}', AdvView),
    web.post('/adv', AdvView),
    web.patch('/adv/{adv_id:\d+}', AdvView),
    web.delete('/adv/{adv_id:\d+}', AdvView),
    # Запрос по всем объявлениям. С помощью стриминг.
    web.get('/advs', get_advs),
    # Вывести все объявления пользователя
    web.get('/advs_owner/{owner_id:\d+}', get_owner_advs),
])

if __name__ == '__main__':
    web.run_app(app)
