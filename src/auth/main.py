import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DATABASE = "todo.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

app = FastAPI(title="Auth Module")

@app.on_event("startup")
def on_startup():
    init_db()

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
def register(user: UserRegister):
    conn = get_db()
    try:
        cursor = conn.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = pwd_context.hash(user.password)
        cursor = conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (user.email, hashed))
        conn.commit()
        user_id = cursor.lastrowid
        access_token = create_access_token(data={"sub": user.email, "user_id": user_id})
        return Token(access_token=access_token, token_type="bearer")
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()

@app.post("/login", response_model=Token)
def login(user: UserLogin):
    conn = get_db()
    try:
        cursor = conn.execute("SELECT * FROM users WHERE email = ?", (user.email,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_dict = dict(row)
        if not pwd_context.verify(user.password, user_dict["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(data={"sub": user.email, "user_id": user_dict["id"]})
        return Token(access_token=access_token, token_type="bearer")
    finally:
        conn.close()
