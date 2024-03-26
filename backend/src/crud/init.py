from src.crud.engine import engine, Base


async def initialise_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
