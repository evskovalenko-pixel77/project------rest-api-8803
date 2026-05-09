import sqlite3
import asyncio
import hashlib
import secrets
from fastapi import FastAPI, HTTPException, Depends, Header, status
from pydantic import BaseModel

app = FastAPI()

DATABASE = 'todo.db'

class UserRegister(BaseModel):
    email: str
    password: str

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            api_token TEXT
        )
    ''')
    conn.close()

@app.on_event('startup')
def startup():
    init_db()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_hex(32)

@app.post('/register', status_code=201)
def register(user: UserRegister):
    conn = get_db()
    try:
        cursor = conn.execute('SELECT id FROM users WHERE email = ?', (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail='Email already registered')
        pwd_hash = hash_password(user.password)
        token = generate_token()
        conn.execute('INSERT INTO users (email, password_hash, api_token) VALUES (?, ?, ?)',
                     (user.email, pwd_hash, token))
        conn.commit()
        return {'email': user.email, 'token': token}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail='Email already registered')
    finally:
        conn.close()

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication scheme')
    token = authorization[len('Bearer '):]
    user = await asyncio.to_thread(_get_user_by_token, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    return user

def _get_user_by_token(token: str):
    conn = get_db()
    try:
        cursor = conn.execute('SELECT id, email FROM users WHERE api_token = ?', (token,))
        user = cursor.fetchone()
        if user:
            return user
        return None
    finally:
        conn.close()
