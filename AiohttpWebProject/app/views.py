from aiohttp import web
from sqlalchemy.sql import text
import sqlalchemy.ext.asyncio
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter


# получение координат по названию города
# название городов ожидаются на русском языке
async def getLocation(name):
    
        async with Nominatim(user_agent="app",
                            adapter_factory=AioHTTPAdapter,) as geolocator:
        
            location = await geolocator.geocode(name, language="ru")  
        
            return location


# запрос на просмотр информации об одном городе
async def getCity(request):
    
    try:
        name = request.rel_url.query['name']
    
        async with request.app['db'].connect() as conn:
            
            res = await conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom) \
                                           FROM cities WHERE name = :name;"),
                                           {"name": name})

            strinn = res.first()

            if strinn:
                    return web.json_response({'name': strinn[0], 'latitude': strinn[1], 'longitude': strinn[2]})
            else:
                    return web.Response(status=404, text="Not Found")
    
    except:
        return web.Response(status=400, text="Something went wrong")


# запрос на добавление информации о городе
async def postCity(request):
    
    try:
        
        data = await request.json()
        name = data.get('name')
        
        res = await getLocation(name)
            
        if res:

            point = 'POINT(' + str(res.longitude) + ' ' + str(res.latitude) + ')'

            async with request.app['db'].connect() as conn:
            
                await conn.execute(text("INSERT INTO cities (the_geom, name) \
                                      VALUES (ST_GeomFromText(:point, 4326), :name);"),
                                      {'point': point, 'name': name})
                await conn.commit()
                
                return web.Response(status=201, text="Created")
        else:
            return web.Response(status=400, text="This a city does not exist")
    
    except:
        return web.Response(status=400, text="Something went wrong")


# запрос на удаление информации о городе
async def delCity(request):
    
    try:
        
        name = request.rel_url.query['name']

        async with request.app['db'].connect() as conn:
            
            await conn.execute(text("DELETE FROM cities \
                                    WHERE name = :name"),
                                    {"name": name})
            await conn.commit()
                
            return web.Response(status=200, text="Ok")
    
    except:
        return web.Response(status=400, text="Something went wrong")
 

# запрос на просмотр информации обо всех городах
async def getCities(request):
    
    try:

        async with request.app['db'].connect() as conn:
            
            res = await conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom) \
                                    FROM cities;"))

            payload = []
            content = {}
            for result in res:
                content = {'name': result[0], 'latitude': result[1], 'longitude': result[2]}
                payload.append(content)
                content = {}

            return web.json_response(payload)
    
    except:
        return web.Response(status=400, text="Something went wrong")



 # запрос на поиск ближайших городов по координатам
async def nearestCities(request):
    
    try:
        
        data = request.rel_url
        
        point = 'POINT(' + data.query['longitude'] + ' ' + data.query['latitude'] + ')'

        async with request.app['db'].connect() as conn:
            
            res = await conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom), ST_DistanceSphere(the_geom, \
                                    ST_GeomFromText(:point, 4326)) AS distance \
                                    FROM cities \
                                    ORDER BY distance \
                                    LIMIT 2;"),
                                    {"point": point})
            await conn.commit()
            
            payload = []
            content = {}
            for result in res:
                content = {'name': result[0], 'latitude': result[1], 'longitude': result[2]}
                payload.append(content)
                content = {}
                
            return web.json_response(payload)
    except:
        return web.Response(status=400, text="Something went wrong")