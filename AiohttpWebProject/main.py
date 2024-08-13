import asyncio
from aiohttp import web


from app.routes import routes
from app.settings import config
from app.accessor import setup


app = web.Application()


def setupAccessor(application):
    setup(application)


def setupConfig(application):
    application["config"] = config


def setupRoutes(application):
    routes(application)


def setupApp(application):
   
   setupConfig(application)
   setupAccessor(application)
   setupRoutes(application)
    

if __name__ == "__main__":
    setupApp(app)
    web.run_app(app, port=config["common"]["port"])
