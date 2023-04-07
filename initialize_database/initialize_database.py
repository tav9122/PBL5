import sqlite3

conn = sqlite3.connect('../PBL5.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE users (
username TEXT PRIMARY KEY,
password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE songs (
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
audio BLOB NOT NULL,
owner TEXT NOT NULL,
FOREIGN KEY (owner) REFERENCES users (username) ON DELETE CASCADE
)
''')

# Add user
cursor.execute('''
INSERT INTO users (username, password)
VALUES ('user', 'user')
''')

def audio_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data

cursor.execute(f'''
INSERT INTO songs (title, audio, owner)
VALUES (?, ?, ?)
''', ('[MV OFFICIAL] CHƯA BAO GIỜ - TRUNG QUÂN - 4K.mp3', audio_to_binary_data(
    '[MV OFFICIAL] CHƯA BAO GIỜ - TRUNG QUÂN - 4K.mp3'), 'user'))

cursor.execute(f'''
INSERT INTO songs (title, audio, owner)
VALUES (?, ?, ?)
''', ('[YamiSora] Requiem - Nao Hiiragi - Vietsub.mp3', audio_to_binary_data(
    '[YamiSora] Requiem - Nao Hiiragi - Vietsub.mp3'), 'user'))

cursor.execute(f'''
INSERT INTO songs (title, audio, owner)
VALUES (?, ?, ?)
''', ('Train - Save Me, San Francisco.mp3', audio_to_binary_data('Train - Save Me, San Francisco.mp3'), 'user'))

conn.commit()

conn.close()