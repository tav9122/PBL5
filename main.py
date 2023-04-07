import sqlite3
from dataclasses import dataclass
from fastapi import FastAPI

app = FastAPI()


@dataclass
class Credentials:
    username: str
    password: str


@app.post("/login")
async def login(credentials: Credentials):
    if check_login(credentials.username, credentials.password):
        return {"result": "success"}
    else:
        return {"result": "failed"}

@app.get("/songs/{username}")
async def get_song_titles(username: str):
    conn = sqlite3.connect('PBL5.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT title FROM songs WHERE owner = ?
    ''', (username,))

    rows = cursor.fetchall()
    titles = [row[0] for row in rows]
    return titles

def check_login(username, password):
    conn = sqlite3.connect('PBL5.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))

    return cursor.fetchone() is not None
