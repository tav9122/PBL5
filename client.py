import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Tk, messagebox
import requests

class LoginForm:
    def __init__(self, master):
        self.master = master
        self.master.title("Please login...")

        # Center the window.
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (500 / 2)
        y = (screen_height / 2) - (500 / 2)
        self.master.geometry(f"500x250+{int(x)}+{int(y)}")

        # Initialize window components.
        self.frame_username = tk.Frame(self.master)
        self.frame_username.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_username = tk.Label(self.frame_username, text="Username: ", borderwidth=0)
        self.label_username.pack(side=tk.LEFT, padx=(13, 0))

        self.entry_username = tk.Entry(self.frame_username, width=30)
        self.entry_username.pack(side=tk.LEFT, padx=(0, 13))

        self.frame_password = tk.Frame(self.master)
        self.frame_password.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_password = tk.Label(self.frame_password, text="Password:  ", borderwidth=0)
        self.label_password.pack(side=tk.LEFT, padx=(13, 0))

        self.entry_password = tk.Entry(self.frame_password, width=30)
        self.entry_password.pack(side=tk.LEFT, padx=(0, 13))

        self.button_login = tk.Button(self.master, text="Login", command=self.login)
        self.button_login.pack(side=tk.TOP, pady=(0, 20))

    def login(self):
        credentials = {
            "username": self.entry_username.get(),
            "password": self.entry_password.get()
        }
        response = requests.post("http://localhost:8000/login", json=credentials)
        if response.json()["result"] == "success":
            messagebox.showinfo("Result", "Login success")
            self.master.withdraw()
            self.main_gui = MusicPlayer(self.master, self.entry_username.get())
        else:
            messagebox.showerror("Result", "Wrong username or password")
            self.entry_password.delete(0, tk.END)


class MusicPlayer:
    def __init__(self, master, username):
        self.master = master
        self.top = tk.Toplevel(self.master)
        self.top.title("Music Player")

        # Center the window.
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width / 2) - (1200 / 2)
        y = (screen_height / 2) - (1100 / 2)
        self.top.geometry(f"1200x775+{int(x)}+{int(y)}")

        # Initialize window components.
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

        self.logout_button = tk.Button(self.top, text=" Log out", command=self.logout)
        self.logout_button.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        response = requests.get(f"http://localhost:8000/songs/{username}")
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

if __name__ == '__main__':
    root = Tk()
    app = LoginForm(root)
    root.mainloop()
