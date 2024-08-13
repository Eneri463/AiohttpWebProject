from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg


def setup(application):
    
    application.on_startup.append(onStart)
    application.on_cleanup.append(onShutdown)


async def onStart(application):
    
    config = application["config"]["postgres"]
    application['db'] = create_async_engine(config["database_url"])


async def onShutdown(application):
    await application['db'].close()
    
