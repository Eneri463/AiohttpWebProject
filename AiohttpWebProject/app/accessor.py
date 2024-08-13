import asyncpgsa


def setup(application):
    
    application.on_startup.append(onStart)
    application.on_cleanup.append(onShutdown)


async def onStart(application):
    
    config = application["config"]["postgres"]
    application['db'] = await asyncpgsa.create_pool(dsn=config["database_url"])


async def onShutdown(application):
    await application['db'].close()
    
