import base64
import os
import tkinter as tk
import time
from random import randint
from tkinter import ttk
import requests
import pygame
from tinytag import TinyTag
import socket
import threading

from SongManagerForm import SongManagerForm


class MusicPlayer:
    def __init__(self, master, username, access_token):
        self.username = username
        self.access_token = access_token
        self.master = master
        self.top = tk.Toplevel(self.master)
        self.top.title("Music Player")

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width / 2) - (700 / 2)
        y = (screen_height / 2) - (600 / 2)
        self.top.geometry(f"700x450+{int(x)}+{int(y)}")

        self.listbox = tk.Listbox(self.top, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.progress_bar = ttk.Scale(self.top, from_=0, to=100, orient=tk.HORIZONTAL, value=0,
                                      command=self.progress_bar_slide, state=tk.DISABLED)
        self.progress_bar.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

        self.status_frame = tk.Frame(self.top)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, ipady=2)

        self.duration_label = tk.Label(self.status_frame, text="00:00", borderwidth=0)
        self.duration_label.pack(side=tk.RIGHT, padx=13)

        self.current_time_label = tk.Label(self.status_frame, text="00:00", borderwidth=0)
        self.current_time_label.pack(side=tk.LEFT, padx=13)

        self.song_title_label = tk.Label(self.status_frame)
        self.song_title_label.pack()

        self.controls_frame = tk.Frame(self.top)
        self.controls_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(25, 0))

        self.play = tk.Button(self.controls_frame, text="Phát", command=self.play_music, state=tk.DISABLED)
        self.play.pack(side=tk.LEFT, padx=10)

        self.pause_resume_button = tk.Button(self.controls_frame, text="Dừng", command=self.pause_resume_music,
                                             state=tk.DISABLED)
        self.pause_resume_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(self.controls_frame, text="Bài tiếp >>", command=self.next_song, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10)

        self.fast_forward_button = tk.Button(self.controls_frame, text=">> 5s", command=self.fast_forward,
                                             state=tk.DISABLED)
        self.fast_forward_button.pack(side=tk.RIGHT, padx=10)

        self.rewind_button = tk.Button(self.controls_frame, text="<< 5s", command=self.rewind,
                                       state=tk.DISABLED)
        self.rewind_button.pack(side=tk.RIGHT, padx=10)

        self.previous_button = tk.Button(self.controls_frame, text="<< Bài trước", command=self.previous_song,
                                         state=tk.DISABLED)
        self.previous_button.pack(side=tk.RIGHT, padx=10)

        self.play_mode_frame = tk.Frame(self.top)
        self.play_mode_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.play_mode_label = tk.Label(self.play_mode_frame, text="Chế độ: ", borderwidth=0)
        self.play_mode_label.pack(side=tk.LEFT, padx=(13, 0))

        self.play_mode_button = tk.Button(self.play_mode_frame, text="Tuần tự", command=self.change_play_mode,
                                          state=tk.DISABLED)
        self.play_mode_button.pack(side=tk.LEFT)

        self.volume_frame = tk.Frame(self.top)
        self.volume_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.volume_label = tk.Label(self.volume_frame, text="Âm lượng: ", borderwidth=0)
        self.volume_label.pack(side=tk.LEFT, padx=13)

        self.volume_bar = ttk.Scale(self.volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, value=1,
                                    command=self.volume_bar_slide, state=tk.DISABLED, length=250)
        self.volume_bar.pack(side=tk.LEFT)

        self.volume_value_label = tk.Label(self.volume_frame, text="100%", borderwidth=0)
        self.volume_value_label.pack(side=tk.LEFT, padx=15)

        self.manage_songs_frame = tk.Frame(self.top)
        self.manage_songs_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0))

        self.manage_songs_button = tk.Button(self.manage_songs_frame, text="Quản lí nhạc",
                                             command=self.show_song_manager)
        self.manage_songs_button.pack(side=tk.LEFT, padx=10)

        self.logout_button = tk.Button(self.top, text=" Đăng xuất", command=self.logout)
        self.logout_button.pack(side=tk.BOTTOM, padx=10, pady=(0, 15))

        self.current_song = None
        self.paused = False
        self.loop_is_running = False
        self.play_mode = "Tuần tự"

        self.get_song_list()
        pygame.mixer.init()

        self.voice_control_thread = threading.Thread(target=self.voice_control)
        self.voice_control_thread.start()

    def play_music(self):
        if self.paused:
            self.pause_resume_music()

        self.current_song = self.get_song(self.listbox.get(self.listbox.curselection()[0]))

        self.progress_bar.config(value=0)
        self.progress_bar.config(to=TinyTag.get(self.current_song).duration)

        self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(0))}")
        self.duration_label.config(
            text=f"{time.strftime('%M:%S', time.gmtime(TinyTag.get(self.current_song).duration))}")

        self.song_title_label.config(text=f"{self.listbox.get(self.listbox.curselection()[0])}")

        if not self.loop_is_running:
            self.loop()

        self.progress_bar.config(state=tk.NORMAL)
        self.volume_bar.config(state=tk.NORMAL)

        pygame.mixer.music.load(self.current_song)
        pygame.mixer.music.play()

    def pause_resume_music(self):

        if self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

            self.paused = False
            self.pause_resume_button.config(text="Dừng")
        else:
            pygame.mixer.music.pause()

            self.paused = True
            self.pause_resume_button.config(text="Tiếp tục")

    def previous_song(self):
        if self.play_mode == "Ngẫu nhiên":
            self.play_shuffle()
            return

        current_index = self.listbox.curselection()[0]

        self.listbox.selection_clear(0, tk.END)

        if current_index > 0:
            self.listbox.selection_set(current_index - 1)

        else:
            self.listbox.selection_set(self.listbox.size() - 1)

        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def next_song(self):
        if self.play_mode == "Ngẫu nhiên":
            self.play_shuffle()
            return

        current_index = self.listbox.curselection()[0]

        self.listbox.selection_clear(0, tk.END)

        if current_index < self.listbox.size() - 1:
            self.listbox.selection_set(current_index + 1)

        else:
            self.listbox.selection_set(0)

        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def fast_forward(self):
        self.progress_bar.config(value=self.progress_bar.get() + 5)

        if self.progress_bar.get() > TinyTag.get(self.current_song).duration:
            self.next_song()

        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def rewind(self):

        self.progress_bar.config(value=self.progress_bar.get() - 5)

        if self.progress_bar.get() < 0:
            self.previous_song()

        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def loop(self):

        self.loop_is_running = True
        if not self.paused:
            song_duration = int(TinyTag.get(self.current_song).duration)

            self.progress_bar.config(value=self.progress_bar.get() + 1)

            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

            if self.progress_bar.get() > song_duration:
                if self.play_mode == "Lặp lại":
                    self.play_music()
                else:
                    self.next_song()

        self.status_frame.after(1000, self.loop)

    def progress_bar_slide(self, _):

        self.progress_bar.config(value=int(self.progress_bar.get()))

        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def volume_bar_slide(self, _):
        pygame.mixer.music.set_volume(self.volume_bar.get())

        self.volume_value_label.config(text=f"{int(pygame.mixer.music.get_volume() * 100)}%")

    def change_play_mode(self):
        if self.play_mode == "Tuần tự":
            self.play_mode = "Lặp lại"
        elif self.play_mode == "Lặp lại":
            self.play_mode = "Ngẫu nhiên"
        else:
            self.play_mode = "Tuần tự"

        self.play_mode_button.config(text=f"{self.play_mode}")

    def play_shuffle(self):
        self.listbox.selection_clear(0, tk.END)

        self.listbox.selection_set(randint(0, self.listbox.size() - 1))

        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def logout(self):
        pygame.mixer.music.stop()
        self.top.destroy()
        self.master.deiconify()

    def show_song_manager(self):
        song_manager_form = SongManagerForm(tk.Toplevel(self.top), self.username, self.access_token)
        self.top.wait_window(song_manager_form.master)
        self.get_song_list()

    def get_song_list(self):
        self.listbox.delete(0, tk.END)
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(f"http://127.0.0.1:8000/{self.username}/songs", headers=headers)

        if response.json():
            self.play.config(state=tk.NORMAL)
            self.pause_resume_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.fast_forward_button.config(state=tk.NORMAL)
            self.rewind_button.config(state=tk.NORMAL)
            self.play_mode_button.config(state=tk.NORMAL)
            self.listbox.selection_set(0)
        else:
            self.play.config(state=tk.DISABLED)
            self.pause_resume_button.config(state=tk.DISABLED)
            self.previous_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.fast_forward_button.config(state=tk.DISABLED)
            self.rewind_button.config(state=tk.DISABLED)
            self.progress_bar.config(state=tk.DISABLED)
            self.progress_bar.config(state=tk.DISABLED)
            self.play_mode_button.config(state=tk.DISABLED)
            return

        for title in response.json():
            self.listbox.insert(tk.END, title)

        if self.current_song:
            self.listbox.selection_set(self.listbox.get(0, tk.END).index(self.current_song.split("/")[-1]))
        else:
            self.listbox.selection_set(0)

    def get_song(self, title):
        if not os.path.exists(f"cache_song/{title}"):
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            response = requests.get(f"http://127.0.0.1:8000/{self.username}/songs/{title}", headers=headers)

            with open(f"cache_song/{title}", "wb") as f:
                f.write(base64.b64decode(response.json()))
        return f"cache_song/{title}"
    
    def voice_control(self):
        HOST = "localhost"
        PORT = 1234
        
        wake_up = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(5)
            while True:
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        data_str = data.decode()
                        print(data_str)
                        if data_str == "Say something..." or data_str == "XXX":
                            continue
                        if data_str == "davit":
                            wake_up = True
                        if wake_up == False:
                            continue
                        elif data_str == "amluongmottram":
                            pygame.mixer.music.set_volume(1)
                            self.volume_value_label.config(text=f"{int(pygame.mixer.music.get_volume() * 100)}%")
                            wake_up = False
                        elif data_str == "amluongnammuoi":
                            pygame.mixer.music.set_volume(0.5)
                            self.volume_value_label.config(text=f"{int(pygame.mixer.music.get_volume() * 100)}%")
                            wake_up = False
                        elif data_str == "baitiep":
                            self.next_song()
                            wake_up = False
                        elif data_str == "baitruoc":
                            self.previous_song()
                            wake_up = False
                        elif data_str == "dung":
                            self.pause_resume_music()
                            wake_up = False
                        elif data_str == "luinamgiay":
                            self.rewind()
                            wake_up = False
                        elif data_str == "phat":
                            self.play_music()
                            wake_up = False
                        elif data_str == "phatlaplai":
                            self.play_mode = "Tuần tự"
                            self.change_play_mode()
                            wake_up = False
                        elif data_str == "phatngaunhien":
                            self.play_mode = "Lặp lại"
                            self.change_play_mode()
                            wake_up = False
                        elif data_str == "phattuantu":
                            self.play_mode = "Ngẫu nhiên"
                            self.change_play_mode()
                            wake_up = False
                        elif data_str == "tatam":
                            pygame.mixer.music.set_volume(0)
                            wake_up = False
                        elif data_str == "toinamgiay":
                            self.fast_forward()

