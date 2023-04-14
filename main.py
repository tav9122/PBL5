import asyncio
import base64
import websockets
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
app = FastAPI()

playback_status = {}


def get_db_cursor():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    return conn.cursor()


class Credentials(BaseModel):
    username: str
    password: str


class Song(BaseModel):
    title: str
    audio: bytes


class AddSongList(BaseModel):
    username: str
    songs: List[Song]


class DeleteSongList(BaseModel):
    username: str
    song_titles: List[str]


@app.post("/login")
async def login(credentials: Credentials):
    cursor = get_db_cursor()

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
    cursor = get_db_cursor()

    try:
        cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            ''', (credentials.username, credentials.password))

        cursor.connection.commit()
        cursor.close()
        return {"result": "success", "message": "Register successfully"}

    except psycopg2.IntegrityError as e:
        cursor.connection.rollback()
        cursor.close()
        return {"result": "failed", "message": "The username is already taken"}


@app.get("/songs/{username}")
async def get_song_titles(username: str):
    cursor = get_db_cursor()

    cursor.execute('''
        SELECT title FROM songs WHERE owner = %s
    ''', [username])

    rows = cursor.fetchall()
    cursor.close()

    if len(rows):
        titles = [row[0] for row in rows]
        return titles
    else:
        return []


async def play_song(websocket, path):
    song_title = await websocket.recv()

    cursor = get_db_cursor()
    cursor.execute('''
        SELECT audio FROM songs WHERE title = %s
    ''', [song_title])
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        audio_data = result[0]
        for i in range(0, len(audio_data), 1024):
            chunk = audio_data[i:i + 1024]
            await websocket.send(base64.b64encode(chunk).decode('utf-8'))

        await websocket.send('Song finished playing')
    else:
        await websocket.send('Song not found')


@app.post("/add-songs")
async def add_songs(add_song_list: AddSongList):
    cursor = get_db_cursor()

    try:
        for song in add_song_list.songs:
            cursor.execute('''
                INSERT INTO songs (title, audio, owner)
                VALUES (%s, %s, %s)
            ''', (song.title, base64.b64decode(song.audio), add_song_list.username))

        cursor.connection.commit()
        cursor.close()
        return {"result": "success", "message": "Songs added successfully"}

    except Exception as e:
        cursor.connection.rollback()
        cursor.close()
        return {"result": "failed", "message": str(e)}


@app.post("/delete-songs")
async def delete_songs(delete_song_list: DeleteSongList):
    cursor = get_db_cursor()

    try:
        for title in delete_song_list.song_titles:
            cursor.execute('''
                DELETE FROM songs WHERE owner = %s AND title = %s
            ''', (delete_song_list.username, title))

        cursor.connection.commit()
        cursor.close()
        return {"result": "success", "message": "Songs deleted successfully"}

    except Exception as e:
        cursor.connection.rollback()
        cursor.close()
        return {"result": "failed", "message": str(e)}


async def websocket_server():
    async with websockets.serve(play_song, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.ensure_future(websocket_server())