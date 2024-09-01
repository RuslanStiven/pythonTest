from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from databases import Database
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

#DATABASE_URL = "postgresql+asyncpg://postgres:170501rusa@127.0.0.1/pythonbase"
DATABASE_URL = "postgresql+asyncpg://postgres:170501rusa@db:5432/pythonbase"

# Асинхронное подключение к базе данных
database = Database(DATABASE_URL)

# Определение метаданных
metadata = MetaData()

# Описание структуры таблицы 'notes'
notes_table = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(50), nullable=False),
    Column("content", String(200), nullable=False),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
)

# Описание структуры таблицы 'users'
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True),
    Column("password_hash", String(100))
)

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)
