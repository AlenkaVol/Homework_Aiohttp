import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        # добавляем нового пользователя
        async with session.post("http://127.0.0.1:8080/user",
                               json={'name': 'Kevin', 'password': 'secret12345'}) as response:
            print(response.status)
            print(await response.text())

        # получаем пользователя по его id
        # async with session.get("http://127.0.0.1:8080/user/1") as response:
        #     print(response.status)
        #     print(await response.text())

        # меняем данные о пользователе
        # async with session.patch("http://127.0.0.1:8080/user/1",
        #                        json={'name': 'Kevin_Junior'}) as response:
        #     print(response.status)
        #     print(await response.text())

        # удаляем пользователя
        # async with session.delete("http://127.0.0.1:8080/user/1") as response:
        #     print(response.status)
        #     print(await response.text())

        # добавляем новое объявление
        # async with session.post("http://127.0.0.1:8080/advertisement",
        #                        json={"title": "Продам машину",
        #                              "description": "Не бита, не крашена!",
        #                              "owner": "2"}) as response:
        #     print(response.status)
        #     print(await response.text())

        # получаем информацию об объявлении
        # async with session.get("http://127.0.0.1:8080/advertisement/1") as response:
        #     print(response.status)
        #     print(await response.text())

        # меняем данные в объявлении
        # async with session.patch("http://127.0.0.1:8080/advertisement/1",
        #                        json={'description': 'Недорого!'}) as response:
        #     print(response.status)
        #     print(await response.text())

        # удаляем объявление
        # async with session.delete("http://127.0.0.1:8080/advertisement/1") as response:
        #     print(response.status)
        #     print(await response.text())


asyncio.run(main())

