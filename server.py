from typing import Type
import bcrypt
from aiohttp import web
from aiohttp.web import HTTPException
from pydantic import ValidationError
from aiohttp.typedefs import Handler
from models import Session, User, engine, Base, Advertisement
from schema import CreateUser, UpdateUser, CreateAdvertisement, UpdateAdvertisement
from sqlalchemy.ext.asyncio import AsyncSession
import json
from sqlalchemy.exc import IntegrityError

app = web.Application()


def hash_password(password: str):
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)


async def orm_context(app):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("FINISH")


app.cleanup_ctx.append(orm_context)


def get_http_error(error_class, message):
    response = json.dumps({'error': message})
    http_error = error_class(text=response, content_type='application/json')
    return http_error


# Функция для получения пользователя по его id
async def get_user_by_id(session, user_id):
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, f'User with id {user_id} not found')
    return user


# Функция для получения объявления по его id
async def get_advertisement_by_id(session, adv_id):
    adv = await session.get(Advertisement, adv_id)
    if adv is None:
        raise get_http_error(web.HTTPNotFound, f'Advertisement with id {adv_id} not found')
    return adv


async def add_user(session, user):
    try:
        session.add(user)
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, f'User with name {user.name} already exists')


async def add_advertisement(session, adv):
    try:
        session.add(adv)
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, f'no such user exists')


@web.middleware
async def http_errors_middleware(request: web.Request, handler: Handler):
    return await handler(request)


@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.middlewares.extend([http_errors_middleware, session_middleware])


class BadRequest(HTTPException):
    status_code = 400

    def __init__(self, description: dict | list | str):
        self.description = description

        super().__init__(
            text=json.dumps({"status": "error", "description": description}),
            content_type="application/json",
        )


def validate(
        model: Type[CreateUser] | Type[UpdateUser] | Type[CreateAdvertisement] | Type[UpdateAdvertisement],
        data: dict
):
    try:
        return model.model_validate(data).model_dump(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise BadRequest(error)


class UserView(web.View):

    @property
    def user_id(self):
        return int(self.request.match_info['user_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_user(self):
        return await get_user_by_id(self.session, self.user_id)

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self):
        json_data = await self.request.json()
        user_data = validate(CreateUser, json_data)
        user_data['password'] = hash_password(user_data['password'])
        user = User(**user_data)
        await add_user(self.session, user)
        user = await get_user_by_id(self.session, user.id)
        return web.json_response(user.dict)

    async def patch(self):
        user = await self.get_user()
        json_data = await self.request.json()
        user_data = validate(UpdateUser, json_data)
        if 'password' in user_data:
            user_data['password'] = hash_password(user_data['password'])
        for field, value in user_data.items():
            setattr(user, field, value)
        await add_user(self.session, user)
        user = await get_user_by_id(self.session, user.id)
        return web.json_response(user.dict)

    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})


class AdvertisementView(web.View):

    @property
    def adv_id(self):
        return int(self.request.match_info['adv_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_advertisement(self):
        return await get_advertisement_by_id(self.session, self.adv_id)

    async def get(self):
        adv = await self.get_advertisement()
        return web.json_response(adv.dict)

    async def post(self):
        json_data = await self.request.json()
        adv_data = validate(CreateAdvertisement, json_data)
        adv = Advertisement(**adv_data)
        await add_advertisement(self.session, adv)
        adv = await get_advertisement_by_id(self.session, adv.id)
        return web.json_response(adv.dict)

    async def patch(self):
        adv = await self.get_advertisement()
        json_data = await self.request.json()
        adv_data = validate(UpdateAdvertisement, json_data)
        for field, value in adv_data.items():
            setattr(adv, field, value)
        await add_advertisement(self.session, adv)
        adv = await get_advertisement_by_id(self.session, adv.id)
        return web.json_response(adv.dict)

    async def delete(self):
        adv = await self.get_advertisement()
        await self.session.delete(adv)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})


app.add_routes(
    [web.get('/user/{user_id:\d+}', UserView),
     web.patch('/user/{user_id:\d+}', UserView),
     web.delete('/user/{user_id:\d+}', UserView),
     web.post('/user', UserView),

     web.get('/advertisement/{adv_id:\d+}', AdvertisementView),
     web.patch('/advertisement/{adv_id:\d+}', AdvertisementView),
     web.delete('/advertisement/{adv_id:\d+}', AdvertisementView),
     web.post('/advertisement', AdvertisementView)]
)


web.run_app(app)
