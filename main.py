import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from typing import List
from models import NoteIn, NoteOut, User, SpellCheckResult, TextToCheck
from database import database, notes_table, users_table
from auth import verify_password, create_access_token, decode_token
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Аутентификация и получение токена
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = select(users_table).where(users_table.c.username == form_data.username)
    user = await database.fetch_one(query)

    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Получение текущего пользователя на основе токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    username = decode_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(users_table).where(users_table.c.username == username)
    user = await database.fetch_one(query)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return User(id=user["id"], username=user["username"])

## Получение всех заметок текущего пользователя
@app.get("/notes/", response_model=List[NoteOut])
async def get_notes(current_user: User = Depends(get_current_user)):
    try:
        query = select(notes_table).where(notes_table.c.user_id == current_user.id)
        notes = await database.fetch_all(query)

        # Убедитесь, что все заметки содержат user_id
        notes_with_user_id = [
            {
                "id": note["id"],
                "title": note["title"],
                "content": note["content"],
                "user_id": note["user_id"]
            }
            for note in notes
        ]

        return notes_with_user_id

    except Exception as e:
        print(f"Ошибка в get_notes: {e}")
        raise HTTPException(status_code=500, detail="Интернал сервер ошибка")
#@app.get("/notes/", response_model=List[NoteOut])
#async def get_notes(current_user: User = Depends(get_current_user)):
#    query = select(notes_table).where(notes_table.c.user_id == current_user.id)
#    return await database.fetch_all(query)
#
@app.post("/notes/", response_model=NoteOut)
async def add_note(note: NoteIn, current_user: User = Depends(get_current_user)):
    try:
        # Проверка орфографии перед добавлением заметки
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://speller.yandex.net/services/spellservice.json/checkText",
                params={"text": note.content}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Ошибка при проверке орфографии")

            spell_check_results = response.json()
            if spell_check_results:
                raise HTTPException(status_code=400, detail=spell_check_results)

        # Вставка заметки в базу данных
        query = notes_table.insert().values(
            title=note.title,
            content=note.content,
            user_id=current_user.id  # Указываем user_id
        )
        last_record_id = await database.execute(query)

        # Возвращаем ответ, соответствующий модели NoteOut
        return {"id": last_record_id, "title": note.title, "content": note.content, "user_id": current_user.id}

    except Exception as e:
        print(f"Ошибка в add_note: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при добавлении заметки")
#    query = notes_table.insert().values(title=note.title, content=note.content)
#    last_record_id = await database.execute(query)
#    return {**note.dict(), "id": last_record_id}

# Добавление новой заметки в базу данных с проверкой орфографии
@app.post("/notes/", response_model=NoteOut)
async def add_note(note: NoteIn):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://speller.yandex.net/services/spellservice.json/checkText",
            params={"text": note.content}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при проверке орфографии")

        spell_check_results = response.json()
        if spell_check_results:
            raise HTTPException(status_code=400, detail=spell_check_results)

    query = notes_table.insert().values(title=note.title, content=note.content)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}



# Маршрут для проверки орфографии произвольного текста
@app.post("/spell_check/", response_model=List[SpellCheckResult])
async def spell_check(text: TextToCheck):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://speller.yandex.net/services/spellservice.json/checkText",
            params={"text": text.text}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при проверке орфографии")

        result = response.json()
        return [
            SpellCheckResult(
                word=error["word"],
                suggestions=error["s"],
                pos=error["pos"],
                len=error["len"],
            )
            for error in result
        ]