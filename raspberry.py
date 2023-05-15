import requests
import sounddevice as sd
from scipy.io.wavfile import write
import socket

RATE = 16000
RECORD_SECONDS = 1.5
SERVER_URL = "http://localhost:8000/predict"
CLIENT_HOST = "localhost"
CLIENT_PORT = 1234

def send_word_to_client(word):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((CLIENT_HOST, CLIENT_PORT))
        s.sendall(word.encode())
        s.close()

while True:
    send_word_to_client("Say something...")
    myrecording = sd.rec(int(RECORD_SECONDS * RATE), channels=1, samplerate=RATE)
    sd.wait()
    write('temp/record.wav', RATE, myrecording)

    with open('temp/record.wav', 'rb') as f:
        response = requests.post(SERVER_URL, files={"file": f})

    predicted_word = response.json().get("predicted_word")
    send_word_to_client(predicted_word)