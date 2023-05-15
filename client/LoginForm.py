import tkinter as tk
from tkinter import messagebox
import requests
from MusicPlayer import MusicPlayer
from RegisterForm import RegisterForm


class LoginForm:
    def __init__(self, master):
        self.master = master
        self.master.title("Xin mời đăng nhập...")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (500 / 2)
        y = (screen_height / 2) - (500 / 2)
        self.master.geometry(f"500x250+{int(x)}+{int(y)}")

        self.username_frame = tk.Frame(self.master)
        self.username_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.username_label = tk.Label(self.username_frame, text="Tài khoản: ", borderwidth=0)
        self.username_label.pack(side=tk.LEFT, padx=(13, 0))

        self.username_entry = tk.Entry(self.username_frame, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=(0, 13))

        self.password_frame = tk.Frame(self.master)
        self.password_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.password_label = tk.Label(self.password_frame, text="Mật khẩu:  ", borderwidth=0)
        self.password_label.pack(side=tk.LEFT, padx=(13, 0))

        self.password_entry = tk.Entry(self.password_frame, width=30, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=(0, 13))

        self.function_frame = tk.Frame(self.master)
        self.function_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_register = tk.Button(self.function_frame, text="Đăng kí", command=self.show_registration_form)
        self.button_register.pack(side=tk.RIGHT, padx=(0, 20))

        self.button_login = tk.Button(self.function_frame, text="Đăng nhập", command=self.login)
        self.button_login.pack(side=tk.RIGHT, padx=(0, 20))

    def show_registration_form(self):
        register_form = RegisterForm(self.master)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Lỗi", "Không được để trống các trường")
            return

        credentials = {
            "username": username,
            "password": password
        }

        response = requests.post("http://127.0.0.1:8000/login", json=credentials)

        if response.json()["result"] == "success":
            messagebox.showinfo("Kết quả", response.json()["message"])
            self.master.withdraw()
            self.main_gui = MusicPlayer(self.master, self.username_entry.get(), response.json()["access_token"])
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", response.json()["message"])
            self.password_entry.delete(0, tk.END)
