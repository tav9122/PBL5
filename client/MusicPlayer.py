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
from playsound import playsound

from SongManagerForm import SongManagerForm

server_url = "192.168.43.224"

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

        self.stop_thread = False    
        self.voice_control_thread = threading.Thread(target=self.voice_control)
        self.voice_control_thread.start()

    def play_music(self):
        """
        Play music
        """

        if self.paused:
            self.pause_resume_music()

        self.current_song = self.get_song(self.listbox.get(self.listbox.curselection()[0]))

        # Reset progress bar to 0
        self.progress_bar.config(value=0)
        self.progress_bar.config(to=TinyTag.get(self.current_song).duration)

        # Reset current time label to 00:00 and max time label to song duration
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
        """
        Pause or resume music
        """
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
        """
        Play previous song
        """
        if self.play_mode == "Ngẫu nhiên":
            self.play_shuffle()
            return

        current_index = self.listbox.curselection()[0]

        self.listbox.selection_clear(0, tk.END)

        # If current song is not the first song in the listbox then play previous song else play last song in the listbox
        if current_index > 0:
            self.listbox.selection_set(current_index - 1)

        else:
            self.listbox.selection_set(self.listbox.size() - 1)

        # Play the song despite of the current state of the music player (paused or not)
        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def next_song(self):
        """
        Play next song
        """
        if self.play_mode == "Ngẫu nhiên":
            self.play_shuffle()
            return

        current_index = self.listbox.curselection()[0]

        self.listbox.selection_clear(0, tk.END)

        # If current song is not the last song in the listbox then play next song else play first song in the listbox
        if current_index < self.listbox.size() - 1:
            self.listbox.selection_set(current_index + 1)

        else:
            self.listbox.selection_set(0)

        # Play the song despite of the current state of the music player (paused or not)
        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def fast_forward(self):
        """
        Fast forward song
        """
        # Increase progress bar value by 5 seconds
        self.progress_bar.config(value=self.progress_bar.get() + 5)

        # If progress bar value is greater than song duration then play next song
        if self.progress_bar.get() > TinyTag.get(self.current_song).duration:
            self.next_song()

        # If music is not paused then play music from the new progress bar value else update current time label
        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def rewind(self):
        """
        Rewind song
        """

        # Decrease progress bar value by 5 seconds
        self.progress_bar.config(value=self.progress_bar.get() - 5)

        # If progress bar value is less than 0 then play previous song
        if self.progress_bar.get() < 0:
            self.previous_song()

        # If music is not paused then play music from the new progress bar value else update current time label
        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def loop(self):
        """
        This loop is to manage the progress bar and the current time label, keep them updated every second
        """

        # This is to prevent the loop from running multiple times.
        self.loop_is_running = True
        if not self.paused:
            song_duration = int(TinyTag.get(self.current_song).duration)

            # Increase progress bar value by 1 second every second
            self.progress_bar.config(value=self.progress_bar.get() + 1)

            # Update current time label every second to match the progress bar value    
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")
            
            # If progress bar value is greater than song duration then play next song if play mode is not "Lặp lại" else play current song again
            if self.progress_bar.get() > song_duration:
                if self.play_mode == "Lặp lại":
                    self.play_music()
                else:
                    self.next_song()

        self.status_frame.after(1000, self.loop)

    def progress_bar_slide(self, _):
        """
        Handle the progress bar slide event
        """
        self.progress_bar.config(value=int(self.progress_bar.get()))

        if not self.paused:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play(start=int(self.progress_bar.get()))

        else:
            self.current_time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(self.progress_bar.get()))}")

    def volume_bar_slide(self, _):
        """
        Handle the volume bar slide event
        """
        pygame.mixer.music.set_volume(self.volume_bar.get())

        self.volume_value_label.config(text=f"{int(pygame.mixer.music.get_volume() * 100)}%")

    def change_play_mode(self):
        """
        Switch between play modes
        """
        if self.play_mode == "Tuần tự":
            self.play_mode = "Lặp lại"
        elif self.play_mode == "Lặp lại":
            self.play_mode = "Ngẫu nhiên"
        else:
            self.play_mode = "Tuần tự"

        self.play_mode_button.config(text=f"{self.play_mode}")

    def play_shuffle(self):
        """
        Play a random song
        """
        self.listbox.selection_clear(0, tk.END)

        self.listbox.selection_set(randint(0, self.listbox.size() - 1))

        status = self.paused
        self.play_music()
        if status:
            self.pause_resume_music()

    def logout(self):
        """
        Log out from the current account
        """

        self.stop_thread = True
        self.voice_control_thread.join(timeout=0.25)
        pygame.mixer.music.stop()

        #Destroy the current window and show the login form
        self.top.destroy()
        self.master.deiconify()
        

    def show_song_manager(self):
        """
        Show the song manager form
        """
        song_manager_form = SongManagerForm(tk.Toplevel(self.top), self.username, self.access_token)
        self.top.wait_window(song_manager_form.master)
        self.get_song_list()

    def get_song_list(self):
        """
        Get the song list from the server via API
        """
        self.listbox.delete(0, tk.END)
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(f"http://{server_url}:8000/{self.username}/songs", headers=headers)

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
        """
        Get the song from the server via API by the given title
        """
        if not os.path.exists(f"cache_song/{title}"):
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            response = requests.get(f"http://{server_url}:8000/{self.username}/songs/{title}", headers=headers)

            with open(f"cache_song/{title}", "wb") as f:
                f.write(base64.b64decode(response.json()))
        return f"cache_song/{title}"
    
    def voice_control(self):
        """
        Handle the voice control by start a thread and listen to the raspberry, to receive the command from it
        """
        HOST = server_url
        PORT = 1234
        
        wake_up = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen(5)
            while True:
                if self.stop_thread:
                    return
                
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
                        if data_str == "meimei":
                            playsound("resources/mixkit-confirmation-tone-2867.wav")
                            wake_up = True
                        if wake_up == False:
                            continue
                        elif data_str == "amluongmottram":
                            self.volume_bar.set(1)
                            wake_up = False
                        elif data_str == "amluongnammuoi":
                            self.volume_bar.set(0.5)
                            wake_up = False
                        elif data_str == "baitieptheo":
                            self.next_song()
                            wake_up = False
                        elif data_str == "baitruocdo":
                            self.previous_song()
                            wake_up = False
                        elif data_str == "dunglai":
                            self.pause_resume_music()
                            wake_up = False
                        elif data_str == "tualui":
                            self.rewind()
                            wake_up = False
                        elif data_str == "batnhac":
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
                            self.volume_bar.set(0)
                            wake_up = False
                        elif data_str == "tuatoi":
                            self.fast_forward()

