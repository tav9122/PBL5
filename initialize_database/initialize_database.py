import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="pbl5",
    user="vu",
    password="vu"
)

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    audio BYTEA NOT NULL,
    owner TEXT NOT NULL,
    FOREIGN KEY (owner) REFERENCES users (username) ON DELETE CASCADE
)
''')

cursor.execute('''
INSERT INTO users (username, password)
VALUES ('user', 'user')
''')


def audio_to_binary_data(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data


cursor.execute('''
INSERT INTO songs (title, audio, owner)
VALUES (%s, %s, %s)
''', ('[MV OFFICIAL] CHƯA BAO GIỜ - TRUNG QUÂN - 4K.wav', audio_to_binary_data(
    '[MV OFFICIAL] CHƯA BAO GIỜ - TRUNG QUÂN - 4K.wav'), 'user'))

cursor.execute('''
INSERT INTO songs (title, audio, owner)
VALUES (%s, %s, %s)
''', ('[YamiSora] Requiem - Nao Hiiragi - Vietsub.wav', audio_to_binary_data(
    '[YamiSora] Requiem - Nao Hiiragi - Vietsub.wav'), 'user'))

cursor.execute('''
INSERT INTO songs (title, audio, owner)
VALUES (%s, %s, %s)
''', ('Train - Save Me, San Francisco.wav', audio_to_binary_data('Train - Save Me, San Francisco.wav'), 'user'))

conn.commit()

conn.close()
