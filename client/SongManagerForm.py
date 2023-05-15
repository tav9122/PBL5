import base64
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests


def is_currently_playing(song_title):
    song_path = f"cache_song/{song_title}"
    try:
        os.rename(song_path, song_path)
        return False
    except OSError:
        return True


def is_in_cache(song_title):
    song_path = f"cache_song/{song_title}"
    return os.path.exists(song_path)


class SongManagerForm:
    def __init__(self, master, username, access_token):
        self.username = username
        self.access_token = access_token
        self.master = master
        self.master.title("Quản lí nhạc")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (600 / 2)
        y = (screen_height / 2) - (500 / 2)
        self.master.geometry(f"600x300+{int(x)}+{int(y)}")

        self.listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE)
        self.listbox.pack(side=tk.TOP, padx=10, fill=tk.BOTH, expand=True)

        self.function_frame = tk.Frame(self.master)
        self.function_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.add_songs_button = tk.Button(self.function_frame, text="Thêm bài hát", command=self.add_songs)
        self.add_songs_button.pack(side=tk.LEFT, padx=10)

        self.delete_songs = tk.Button(self.function_frame, text="Xóa bài hát", command=self.delete_songs)
        self.delete_songs.pack(side=tk.LEFT, padx=10)

        self.get_song_list()

    def add_songs(self):
        file_types = [('Music Files', """*.mp3 *.mp4 *.m4a *.m4b *.m4r *.m4v *.alac *.aax *.aaxc *.wav *.ogg *.opus 
        *.flac *.wma""")]
        song_paths = filedialog.askopenfilenames(title="Chọn các bài hát", filetypes=file_types)

        if len(song_paths) == 0:
            return

        songs = []
        duplicate_songs = []
        for song_path in song_paths:
            with open(song_path, 'rb') as f:
                audio_data = f.read()

            song_title = song_path.split('/')[-1]

            if song_title in self.listbox.get(0, tk.END):
                duplicate_songs.append(f'"{song_title}"')
                continue

            song = {
                'title': song_title,
                'audio': base64.b64encode(audio_data).decode('utf-8')
            }
            songs.append(song)

        if duplicate_songs:
            messagebox.showerror("Error", f"Các bài lặp lại: {', '.join(duplicate_songs)} sẽ không được thêm")

        if len(songs) == 0:
            return

        data = {
            'username': self.username,
            'songs': songs
        }
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.post("http://127.0.0.1:8000/add-songs", json=data, headers=headers)
        if response.json()["result"] == "success":
            messagebox.showinfo("Kết quả", response.json()["message"])
            self.get_song_list()
        else:
            messagebox.showerror("Kết quả", response.json()["message"])

    def delete_songs(self):
        selected_songs = self.listbox.curselection()
        if len(selected_songs) == 0:
            messagebox.showerror("Lỗi", "Chọn ít nhất một bài để xóa")
            return

        song_titles = []
        current_playing_song = None
        for idx in selected_songs:
            song_title = self.listbox.get(idx)
            if is_in_cache(song_title) and is_currently_playing(song_title):
                current_playing_song = song_title
                continue
            song_titles.append(song_title)

        if current_playing_song:
            messagebox.showerror("Lỗi", f"Sẽ không xóa {current_playing_song} vì bài hát đang được phát")

        data = {
            'username': self.username,
            'song_titles': song_titles
        }
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.post("http://127.0.0.1:8000/delete-songs", json=data, headers=headers)

        if response.json()["result"] == "success":
            messagebox.showinfo("Kết quả", response.json()["message"])
            for song_title in song_titles:
                song_path = f"cache_song/{song_title}"
                if is_in_cache(song_title):
                    os.remove(song_path)
            self.get_song_list()
        else:
            messagebox.showerror("Kết quả", response.json()["message"])

    def get_song_list(self):
        self.listbox.delete(0, tk.END)
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.get(f"http://127.0.0.1:8000/{self.username}/songs", headers=headers)
        for title in response.json():
            self.listbox.insert(tk.END, title)
