from aiohttp import ClientSession
from asyncio import run


async def main():
    # С помощью менеджера контекста создаём экземпляр класса сессия.
    async with ClientSession() as session:
        # # get запрос для вьюхи и маршрута hello_world
        # response = await session.get('http://127.0.0.1:8080/hello_world')

############# Запросы по пользователям (по таблице Users) ############
        # Post запрос для создания пользователя
        response = await session.post('http://127.0.0.1:8080/user', json={
            'email': 'user1@mail.ru',
            'password': '12345678'
        })
        print(response.status)
        print(await response.json())

        # # Post запрос для url /login' для проверки юзера и пароля. Get тоже работает.
        # response = await session.post('http://127.0.0.1:8080/login', json={
        #     'email': 'user8@yandex.ru',
        #     'password': '12345678'
        # })
        # print(response.status)
        # print(await response.json())

        # # Get запрос.
        # response = await session.get('http://127.0.0.1:8080/user/1')
        # print(response.status)
        # print(await response.json())

        # # Patch запрос. Меняем email пользователя.
        # response = await session.patch('http://127.0.0.1:8080/user/11', json={
        #     'email': 'dsfs@df.df'
        # })
        # print(response.status)
        # print(await response.json())

        # # Patch запрос. Меняем пароль пользователя.
        # response = await session.patch('http://127.0.0.1:8080/user/1', json={
        #     'password': '12345678'
        # })
        # print(response.status)
        # print(await response.json())

        # # Patch запрос. Меняем email и пароль пользователя.
        # response = await session.patch('http://127.0.0.1:8080/user/11', json={
        #     'email': 'mail11@mail.ru',
        #     'password': '123456789'
        # })
        # print(response.status)
        # print(await response.json())

        # # Delete запрос.
        # response = await session.delete('http://127.0.0.1:8080/user/10')
        #
        # print(response.status)
        # print(await response.json())


        # # Get запрос.
        # response = await session.get('http://127.0.0.1:8080/user/3')
        #
        # print(response.status)
        # print(await response.json())

        # # Демонстрация пагинации из лекции для запроса swapi
        # response = await session.get('https://swapi.dev/api/people')
        # data = await response.json()
        # print(data)

        # # Запрос get по всем пользователям
        # response = await session.get('http://127.0.0.1:8080/users')
        # print(response.status)
        # async for line in response.content:
        #     print(line.decode("unicode-escape"))


############# Запросы по объявлениям (по таблице Adv) ################

        # # Post запрос для создания объявления
        # response = await session.post('http://127.0.0.1:8080/adv', json={
        #     'title': 'Продам iphone',
        #     'message': 'iphone 14',
        #     'owner': 'Яблочник',
        #     'owner_id': 11,
        # })
        # print(response.status)
        # print(await response.json())

        # # Patch запрос. Меняем содержание объявления.
        # response = await session.patch('http://127.0.0.1:8080/adv/4', json={
        #     'title': 'Xiaomi', 'message': 'Super 20 Pro'
        # })
        # print(response.status)
        # print(await response.json())

        # # Delete запрос.
        # response = await session.delete('http://127.0.0.1:8080/adv/5')
        #
        # print(response.status)
        # print(await response.json())

        # # Get запрос.
        # response = await session.get('http://127.0.0.1:8080/adv/1')
        # print(response.status)
        # print(await response.json())

        # # Запрос get по всем объявлениям
        # response = await session.get('http://127.0.0.1:8080/advs')
        # print(response.status)
        # async for line in response.content:
        #     print(line.decode("unicode-escape"))

        # # Get запрос - вывести все объявления пользователя, id которого указан в url-e
        # response = await session.get('http://127.0.0.1:8080/advs_owner/11')
        # print(response.status)
        # async for line in response.content:
        #     # https://stackoverflow.com/questions/6504200/how-to-decode-unicode-raw-literals-to-readable-string
        #     # Долго боролся с отображением кириллицы
        #     print(line.decode("unicode-escape"))

run(main())