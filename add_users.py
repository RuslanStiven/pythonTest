import asyncio
from database import database, users_table
from auth import get_password_hash
from sqlalchemy import insert


# Функция для добавления пользователя
async def add_user(username: str, password: str):
    password_hash = get_password_hash(password)
    query = insert(users_table).values(username=username, password_hash=password_hash)
    await database.execute(query)


# Основная функция для добавления предустановленных пользователей
async def main():
    await database.connect()

    # Добавляем нескольких предустановленных пользователей
    await add_user("user0", "password0")
    await add_user("user1", "password1")
    await add_user("user2", "password2")
    await add_user("user3", "password3")
    await add_user("user4", "password4")
    await add_user("user5", "password5")
    await add_user("user6", "password6")
    await add_user("user7", "password7")
    await add_user("user8", "password8")
    await add_user("user9", "password9")

    await database.disconnect()


# Запускаем скрипт
asyncio.run(main())