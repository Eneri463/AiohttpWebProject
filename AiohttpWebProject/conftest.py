import pytest
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

from app.settings import config
from app.routes import routes


pytest_plugins = 'aiohttp.pytest_plugin'


async def createdb():
     
    engine = create_async_engine(config["postgres"]["test_database_url"])
    
    try:
        async with engine.connect() as conn:
            await conn.execute(text("DROP TABLE cities"))
            await conn.commit()
    except:
        pass
    
    async with engine.connect() as conn:
            
            await conn.execute(text("CREATE TABLE cities( \
                                    id SERIAL PRIMARY KEY, \
                                    name varchar(50) NOT NULL UNIQUE, \
                                    the_geom geometry(POINT,4326) NOT NULL \
                                    );"))
            await conn.execute(text("INSERT INTO cities (the_geom, name) \
                                     VALUES (ST_GeomFromText('POINT(82.9226887 55.0288307)', \
                                    4326), 'Новосибирск');"))
            await conn.commit()


def create_app():
    
    app = web.Application()
    routes(app)
    app['db'] = create_async_engine(config["postgres"]["test_database_url"])
    
    return app

    
@pytest.fixture
async def cli(aiohttp_client):
    await createdb()
    app = create_app()
    return await aiohttp_client(app)

# GET информация о городе (корректный ввод)
async def test_get_city_ok(cli):
    
    resp = await cli.get('/city?name=Новосибирск')
    assert resp.status == 200
 

# GET информация о городе (города нет в базе)
async def test_get_city_not_found(cli):
    
    resp = await cli.get('/city?name=Москва')
    assert resp.status == 404


# GET информация о городе (ошибка в запросе)
async def test_get_city_wrong(cli):
    
    resp = await cli.get('/city?view=Москва')
    assert resp.status == 400


# GET информация обо всех городах (корректный ввод)
async def test_get_all_cities(cli):
    
    resp = await cli.get('/cities')
    assert resp.status == 200


# GET информация о двух ближайших городах (корректный запрос)
async def test_get_nearest_cities(cli):
    
    resp = await cli.get('/nearestCities?longitude=92.872586&latitude=56.0091173')
    assert resp.status == 200


# GET информация о двух ближайших городах (ошибка в запросе)
async def test_get_nearest_cities_wrong(cli):
    
    resp = await cli.get('/nearestCities?longitude=92.872586')
    assert resp.status == 400


# POST добавление города в базу (корректный запрос, добавляется существующий город)
async def test_post_city(cli):
    
    resp = await cli.post('/city', json={'name': 'Омск'})
    assert resp.status == 201


# POST добавление города в базу (корректный запрос, добавляется не существующий город)
async def test_post_city_not_exist(cli):
    
    resp = await cli.post('/city', json={'name': 'Гороод'})
    assert resp.status == 400
    assert await resp.text() == "This a city does not exist"


# POST добавление города в базу (некорректный запрос)
async def test_post_city_wrong(cli):
    
    resp = await cli.post('/city', json={'namee': 'Томск'})
    assert resp.status == 400
    assert await resp.text() == "Something went wrong"

    

