import base64
from typing import List
import psycopg2
from dataclasses import dataclass
from fastapi import FastAPI

app = FastAPI()


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class Song:
    title: str
    audio: bytes


@dataclass
class AddSongList:
    username: str
    songs: List[Song]


@dataclass
class DeleteSongList:
    username: str
    song_titles: List[str]


@app.post("/login")
async def login(credentials: Credentials):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE username = %s AND password = %s
    ''', (credentials.username, credentials.password))

    result = cursor.fetchone()

    if result is not None:
        return {"result": "success", "message": "Login successfully"}
    else:
        return {"result": "failed", "message": "Wrong username or password"}


@app.post("/register")
async def register(credentials: Credentials):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    cursor = conn.cursor()

    try:
        cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            ''', (credentials.username, credentials.password))

        conn.commit()
        conn.close()
        return {"result": "success", "message": "Register successfully"}

    except psycopg2.IntegrityError as e:
        conn.rollback()
        conn.close()
        return {"result": "failed", "message": "The username is already taken"}


@app.get("/songs/{username}")
async def get_song_titles(username: str):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title FROM songs WHERE owner = %s
    ''', [username])

    rows = cursor.fetchall()
    conn.close()

    if len(rows):
        titles = [row[0] for row in rows]
        return titles
    else:
        return []



@app.post("/add-songs")
async def add_songs(add_song_list: AddSongList):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    cursor = conn.cursor()

    try:
        for song in add_song_list.songs:
            cursor.execute('''
                INSERT INTO songs (title, audio, owner)
                VALUES (%s, %s, %s)
            ''', (song.title, base64.b64decode(song.audio), add_song_list.username))

        conn.commit()
        conn.close()
        return {"result": "success", "message": "Songs added successfully"}

    except Exception as e:
        conn.rollback()
        conn.close()
        return {"result": "failed", "message": str(e)}


@app.post("/delete-songs")
async def delete_songs(delete_song_list: DeleteSongList):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    cursor = conn.cursor()

    try:
        for title in delete_song_list.song_titles:
            cursor.execute('''
                DELETE FROM songs WHERE owner = %s AND title = %s
            ''', (delete_song_list.username, title))

        conn.commit()
        conn.close()
        return {"result": "success", "message": "Songs deleted successfully"}

    except Exception as e:
        conn.rollback()
        conn.close()
        return {"result": "failed", "message": str(e)}
