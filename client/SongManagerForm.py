import base64
import tkinter as tk
from tkinter import filedialog, messagebox
import requests


class SongManagerForm:
    def __init__(self, master, username):
        self.username = username
        self.master = master
        self.master.title("Music Manager")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (1200 / 2)
        y = (screen_height / 2) - (700 / 2)
        self.master.geometry(f"1200x575+{int(x)}+{int(y)}")

        self.listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE)
        self.listbox.pack(side=tk.TOP, padx=10, fill=tk.BOTH, expand=True)

        self.function_frame = tk.Frame(self.master)
        self.function_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.add_songs_button = tk.Button(self.function_frame, text="Add songs", command=self.add_songs)
        self.add_songs_button.pack(side=tk.LEFT, padx=10)

        self.delete_songs = tk.Button(self.function_frame, text="Delete songs", command=self.delete_songs)
        self.delete_songs.pack(side=tk.LEFT, padx=10)

        response = requests.get(f"http://localhost:8000/songs/{self.username}")

        for title in response.json():
            self.listbox.insert(tk.END, title)

    def add_songs(self):
        file_types = [('Music Files', """*.mp3 *.mp4 *.m4a *.m4b *.m4r *.m4v *.alac *.aax *.aaxc *.wav *.ogg *.opus 
        *.flac *.wma""")]
        song_paths = filedialog.askopenfilenames(title="Choose songs", filetypes=file_types)

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
            messagebox.showerror("Error", f"Duplicate songs: {', '.join(duplicate_songs)} won't be added")

        if len(songs) == 0:
            return

        data = {
            'username': self.username,
            'songs': songs
        }

        response = requests.post("http://localhost:8000/add-songs", json=data)
        if response.json()["result"] == "success":
            messagebox.showinfo("Result", response.json()["message"])

            response = requests.get(f"http://localhost:8000/songs/{self.username}")
            self.listbox.delete(0, tk.END)
            for title in response.json():
                self.listbox.insert(tk.END, title)
        else:
            messagebox.showerror("Result", response.json()["message"])

    def delete_songs(self):
        selected_songs = self.listbox.curselection()
        if len(selected_songs) == 0:
            messagebox.showerror("Error", "Choose at least 1 song to delete")
            return

        song_titles = [self.listbox.get(idx) for idx in selected_songs]
        data = {
            'username': self.username,
            'song_titles': song_titles
        }

        response = requests.post("http://localhost:8000/delete-songs", json=data)
        if response.json()["result"] == "success":
            messagebox.showinfo("Result", response.json()["message"])

            response = requests.get(f"http://localhost:8000/songs/{self.username}")
            self.listbox.delete(0, tk.END)
            for title in response.json():
                self.listbox.insert(tk.END, title)
        else:
            messagebox.showerror("Result", response.json()["message"])
