import base64
import psycopg2
from fastapi import FastAPI, Depends, File, UploadFile
from pydantic import BaseModel
from typing import List
from fastapi_jwt_auth import AuthJWT
import pickle
import math
import librosa
import numpy as np
from pydub import AudioSegment, effects
from scipy.io.wavfile import write, read

app = FastAPI()

class Settings(BaseModel):
    authjwt_secret_key:str = "1cf5449ad63af61cabb6c6ad655062ca45d53aa8e174f052802dd0df4fb75885"
    authjwt_token_expires:int = 3600

@AuthJWT.load_config
def get_config():
    return Settings()

def get_db_cursor():
    """
    This function returns a cursor object for a database connection.
    @return A cursor object for a database connection.
    """
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="pbl5",
        user="vu",
        password="vu"
    )
    return conn.cursor()

model = {}

class_names =  ['amluongmottram', 'amluongnammuoi', 'baitieptheo','baitruocdo','batnhac','dunglai','meimei','phatlaplai','phatngaunhien','phattuantu','tatam','tualui','tuatoi']
audio_format = 'wav'

record_path = 'temp/record.wav'
trimmed_path = 'temp/trimmed.wav'
model_path = 'new_model_5'

for key in class_names:
    name = f"{model_path}/model_{key}.pkl"
    with open(name, 'rb') as file:
        model[key] = pickle.load(file)

def get_mfcc(file_path):
    """
    Given a file path, extract the Mel-frequency cepstral coefficients (MFCC) from the audio file.
    @param file_path - the path to the audio file
    @return The MFCC of the audio file.
    """
    y, sr = librosa.load(file_path)
       
    hop_length = math.floor(sr * 0.010)
    win_length = math.floor(sr * 0.025)
    mfcc = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=12, n_fft=1024,
        hop_length=hop_length, win_length=win_length)
    mfcc = mfcc - np.mean(mfcc, axis=1).reshape((-1, 1))
    delta1 = librosa.feature.delta(mfcc, order=1)
    delta2 = librosa.feature.delta(mfcc, order=2)
    X = np.concatenate([mfcc, delta1, delta2], axis=0)  # O^r
    return X.T 


def detect_leading_silence(sound, silence_threshold=-19.0, chunk_size=10):
    """
    Given a sound file, detect the amount of leading silence in the file.
    @param sound - the sound file
    @param silence_threshold - the threshold below which a chunk is considered silent
    @param chunk_size - the size of the chunks to split the sound file into
    @return the duration of the leading silence in seconds
    """
    trim_ms = 0
    assert chunk_size > 0
    while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms


def predict(file_name=None):
    """
    Given a file path, predict the word spoken in the audio file.
    """
    if not file_name:
        file_name = record_path
        
    trimmed_path = 'temp/trimmed.wav'
    sound = AudioSegment.from_file(file_name, format='wav')
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)

    if start_trim >= 800 or duration - end_trim - start_trim < 100:
        return "XXX"
    normalizedsound = effects.normalize(sound)
    normalizedsound.export(trimmed_path, format='wav')
    
    rate, data = read(trimmed_path)
    write(trimmed_path, rate, data)
    
    sound = AudioSegment.from_file(trimmed_path, format='wav')
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)
    trimmed_sound = sound[start_trim:duration - end_trim]
    trimmed_sound.export(trimmed_path, format='wav')

    if start_trim >= 800:
        return "XXX"
    record_mfcc = get_mfcc(trimmed_path)
    scores = [model[cname].score(record_mfcc) for cname in class_names]
    predict_word = np.argmax(scores)
    return class_names[predict_word]


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
async def login(credentials: Credentials,Authorize: AuthJWT=Depends()):
    """
    This function handles the login process.
    @param credentials - the username and password of the user
    @return A message indicating whether the login was successful or not.
    """
    cursor = get_db_cursor()

    cursor.execute('''
        SELECT * FROM users WHERE username = %s AND password = %s
    ''', (credentials.username, credentials.password))

    result = cursor.fetchone()

    if result is not None:
        return {"result": "success", "message": "Đăng nhập thành công", "access_token": Authorize.create_access_token(subject=credentials.username)}
    else:
        return {"result": "failed", "message": "Sai tài khoản hoặc mật khẩu", "access_token": None}


@app.post("/register")
async def register(credentials: Credentials):
    """
    This function handles the registration process.
    @param credentials - the username and password of the user
    @return A message indicating whether the registration was successful or not.
    """
    cursor = get_db_cursor()

    try:
        cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            ''', (credentials.username, credentials.password))

        cursor.connection.commit()
        cursor.close()
        return {"result": "success", "message": "Đăng kí thành công"}

    except psycopg2.IntegrityError as e:
        cursor.connection.rollback()
        cursor.close()
        return {"result": "failed", "message": "Tên đã có người sử dụng"}


@app.get("/{username}/songs")
async def get_song_titles(username: str, Authorize: AuthJWT=Depends()):
    """
    This function handles the retrieval of the song titles of a user.
    @param username - the username of the user
    @return A list of song titles.
    """
    try :
        Authorize.jwt_required()
    except Exception as e:
        return {"result": "failed", "message": "Bạn chưa đăng nhập"}

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


@app.get("/{username}/songs/{title}")
async def get_song(username: str, title: str, Authorize: AuthJWT=Depends()):
    """
    This function handles the retrieval of a song of a user.
    @param username - the username of the user
    @param title - the title of the song
    @return The audio of the song.
    """
    try :
        Authorize.jwt_required()
    except Exception as e:
        return {"result": "failed", "message": "Bạn chưa đăng nhập"}
    
    cursor = get_db_cursor()

    cursor.execute('''
        SELECT audio FROM songs WHERE owner = %s AND title = %s
    ''', (username, title))

    row = cursor.fetchone()
    cursor.close()

    if row is not None:
        return base64.b64encode(row[0]).decode('utf-8')
    else:
        return None


@app.post("/add-songs")
async def add_songs(add_song_list: AddSongList, Authorize: AuthJWT=Depends()):
    """
    This function handles the addition of songs to the database.
    @param add_song_list - the list of songs to be added
    @return A message indicating whether the addition was successful or not.
    """
    try :
        Authorize.jwt_required()
    except Exception as e:
        return {"result": "failed", "message": "Bạn chưa đăng nhập"}
    
    cursor = get_db_cursor()

    try:
        for song in add_song_list.songs:
            cursor.execute('''
                INSERT INTO songs (title, audio, owner)
                VALUES (%s, %s, %s)
            ''', (song.title, base64.b64decode(song.audio), add_song_list.username))

        cursor.connection.commit()
        cursor.close()
        return {"result": "success", "message": "Thêm bài hát thành công"}

    except Exception as e:
        cursor.connection.rollback()
        cursor.close()
        return {"result": "failed", "message": str(e)}


@app.post("/delete-songs")
async def delete_songs(delete_song_list: DeleteSongList, Authorize: AuthJWT=Depends()):
    """
    This function handles the deletion of songs from the database.
    @param delete_song_list - the list of songs to be deleted
    @return A message indicating whether the deletion was successful or not.
    """
    try :
        Authorize.jwt_required()
    except Exception as e:
        return {"result": "failed", "message": "Bạn chưa đăng nhập"}
    
    cursor = get_db_cursor()

    try:
        for title in delete_song_list.song_titles:
            cursor.execute('''
                DELETE FROM songs WHERE owner = %s AND title = %s
            ''', (delete_song_list.username, title))

        cursor.connection.commit()
        cursor.close()
        return {"result": "success", "message": "Xóa bài hát thành công"}

    except Exception as e:
        cursor.connection.rollback()
        cursor.close()
        return {"result": "failed", "message": str(e)}


@app.post("/predict")
async def create_upload_file(file: UploadFile = File(...)):
    """
    This function handles the prediction of the word in the audio file.
    @param file - the audio file
    @return The predicted word.
    """
    with open("temp/record.wav", "wb") as f:
        contents = await file.read()
        f.write(contents)
    return {"predicted_word": predict("temp/record.wav")}
