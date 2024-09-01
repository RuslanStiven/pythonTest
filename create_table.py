from sqlalchemy.ext.asyncio import create_async_engine
from database import metadata

#DATABASE_URL = "postgresql+asyncpg://postgres:170501rusa@127.0.0.1/pythonbase"
DATABASE_URL = "postgresql+asyncpg://postgres:170501rusa@db:5432/pythonbase"

engine = create_async_engine(DATABASE_URL, echo=True)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

import asyncio
asyncio.run(create_tables())
