import tkinter as tk
from tkinter import ttk
import requests
from SongManagerForm import SongManagerForm


class MusicPlayer:
    def __init__(self, master, username):
        self.username = username
        self.master = master
        self.top = tk.Toplevel(self.master)
        self.top.title("Music Player")

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width / 2) - (1200 / 2)
        y = (screen_height / 2) - (1000 / 2)
        self.top.geometry(f"1200x850+{int(x)}+{int(y)}")

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

        self.play = tk.Button(self.controls_frame, text="Play", command=self.play_music, state=tk.DISABLED)
        self.play.pack(side=tk.LEFT, padx=10)

        self.pause_resume_button = tk.Button(self.controls_frame, text="Pause", command=self.pause_resume_music,
                                             state=tk.DISABLED)
        self.pause_resume_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(self.controls_frame, text="Next >>", command=self.next_song, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10)

        self.skip_forward_button = tk.Button(self.controls_frame, text=">> 5s", command=self.skip_forward,
                                             state=tk.DISABLED)
        self.skip_forward_button.pack(side=tk.RIGHT, padx=10)

        self.skip_backward_button = tk.Button(self.controls_frame, text="<< 5s", command=self.skip_backward,
                                              state=tk.DISABLED)
        self.skip_backward_button.pack(side=tk.RIGHT, padx=10)

        self.previous_button = tk.Button(self.controls_frame, text="<< Previous", command=self.previous_song,
                                         state=tk.DISABLED)
        self.previous_button.pack(side=tk.RIGHT, padx=10)

        self.play_mode_frame = tk.Frame(self.top)
        self.play_mode_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.play_mode_label = tk.Label(self.play_mode_frame, text="Play mode: ", borderwidth=0)
        self.play_mode_label.pack(side=tk.LEFT, padx=(13, 0))

        self.play_mode_button = tk.Button(self.play_mode_frame, text="Sequence", command=self.change_play_mode,
                                          state=tk.DISABLED)
        self.play_mode_button.pack(side=tk.LEFT)

        self.volume_frame = tk.Frame(self.top)
        self.volume_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.volume_label = tk.Label(self.volume_frame, text="Volume: ", borderwidth=0)
        self.volume_label.pack(side=tk.LEFT, padx=13)

        self.volume_bar = ttk.Scale(self.volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, value=1,
                                    command=self.volume_bar_slide, state=tk.DISABLED, length=250)
        self.volume_bar.pack(side=tk.LEFT)

        self.volume_value_label = tk.Label(self.volume_frame, text="100%", borderwidth=0)
        self.volume_value_label.pack(side=tk.LEFT, padx=15)

        self.manage_songs_frame = tk.Frame(self.top)
        self.manage_songs_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0))

        self.manage_songs_button = tk.Button(self.manage_songs_frame, text="Manage songs",
                                             command=self.show_song_manager)
        self.manage_songs_button.pack(side=tk.LEFT, padx=10)

        self.logout_button = tk.Button(self.top, text=" Log out", command=self.logout)
        self.logout_button.pack(side=tk.BOTTOM, padx=10, pady=(0, 15))

        response = requests.get(f"http://localhost:8000/songs/{self.username}")
        for title in response.json():
            self.listbox.insert(tk.END, title)

    def play_music(self):
        pass

    def pause_resume_music(self):
        pass

    def previous_song(self):
        pass

    def next_song(self):
        pass

    def skip_forward(self):
        pass

    def skip_backward(self):
        pass

    def loop(self):
        pass

    def progress_bar_slide(self, _):
        pass

    def volume_bar_slide(self, _):
        pass

    def change_play_mode(self):
        pass

    def play_shuffle(self):
        pass

    def logout(self):
        self.top.destroy()
        self.master.deiconify()

    def show_song_manager(self):
        song_manager_form = SongManagerForm(tk.Toplevel(self.top), self.username)
        self.top.wait_window(song_manager_form.master)

        self.listbox.delete(0, tk.END)
        response = requests.get(f"http://localhost:8000/songs/{self.username}")

        for title in response.json():
            self.listbox.insert(tk.END, title)
