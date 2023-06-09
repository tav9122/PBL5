import requests
import sounddevice as sd
from scipy.io.wavfile import write
import socket
import RPi.GPIO as GPIO
import time
import threading

AWAKE_LED_PIN = 26
LOOP_LED_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(AWAKE_LED_PIN, GPIO.OUT)
GPIO.setup(LOOP_LED_PIN, GPIO.OUT)
RATE = 16000
RECORD_SECONDS = 1.5
SERVER_URL = "http://192.168.43.224:8000/predict"
CLIENT_HOST = "192.168.43.224"
CLIENT_PORT = 1234

def send_word_to_client(word):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((CLIENT_HOST, CLIENT_PORT))
        s.sendall(word.encode())
        s.close()
def turn_off_awake_led():
        time.sleep(1)
        GPIO.output(AWAKE_LED_PIN, GPIO.LOW)
def turn_off_loop_led():
        time.sleep(0.1)
        GPIO.output(LOOP_LED_PIN, GPIO.LOW)
while True:
        send_word_to_client("Say something...")
        GPIO.output(LOOP_LED_PIN, GPIO.HIGH)
        threading.Thread(target=turn_off_loop_led).start()
        myrecording = sd.rec(int(RECORD_SECONDS * RATE), channels=1, samplerate=RATE)
        sd.wait()
        write('temp/record.wav', RATE, myrecording)

        with open('temp/record.wav', 'rb') as f:
                response = requests.post(SERVER_URL, files={"file": f})

        predicted_word = response.json().get("predicted_word")
        send_word_to_client(predicted_word)
        if predicted_word == "meimei":
                GPIO.output(AWAKE_LED_PIN, GPIO.HIGH)
                threading.Thread(target=turn_off_awake_led).start()