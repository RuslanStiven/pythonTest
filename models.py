from pydantic import BaseModel
from typing import List, Optional

# Модель данных для создания заметок
class NoteIn(BaseModel):
    title: str
    content: str

# Модель данных для ответа, включая ID
class NoteOut(NoteIn):
    id: int
    user_id: int  # Добавляем поле user_id, чтобы знать, кому принадлежит заметка

# Модель данных для пользователей
class User(BaseModel):
    id: int
    username: str

# Модель для аутентификации
class TokenData(BaseModel):
    username: Optional[str] = None

# Модель для проверки орфографии
class SpellCheckResult(BaseModel):
    word: str
    suggestions: List[str]
    pos: Optional[int] = None
    len: Optional[int] = None

# Модель для текста, который нужно проверить
class TextToCheck(BaseModel):
    text: str
    language: Optional[str] = "ru"  # Язык текста