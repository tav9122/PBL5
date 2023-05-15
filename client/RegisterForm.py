import tkinter as tk
from tkinter import messagebox
import requests


class RegisterForm:
    def __init__(self, master):
        self.master = master
        self.register_window = tk.Toplevel(self.master)
        self.register_window.title("Mời bạn đăng kí")

        screen_width = self.register_window.winfo_screenwidth()
        screen_height = self.register_window.winfo_screenheight()
        x = (screen_width / 2) - (400 / 2)
        y = (screen_height / 2) - (250 / 2)
        self.register_window.geometry(f"400x250+{int(x)}+{int(y)}")

        self.register_username_frame = tk.Frame(self.register_window)
        self.register_username_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.register_username_label = tk.Label(self.register_username_frame, text="Tài khoản: ", borderwidth=0)
        self.register_username_label.pack(side=tk.LEFT, padx=(13, 0))

        self.register_username_entry = tk.Entry(self.register_username_frame, width=30)
        self.register_username_entry.pack(side=tk.LEFT, padx=(0, 13))

        self.register_password_frame = tk.Frame(self.register_window)
        self.register_password_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.register_password_label = tk.Label(self.register_password_frame, text="Mật khẩu:  ", borderwidth=0)
        self.register_password_label.pack(side=tk.LEFT, padx=(13, 0))

        self.register_password_entry = tk.Entry(self.register_password_frame, width=30)
        self.register_password_entry.pack(side=tk.LEFT, padx=(0, 13))

        self.confirm_password_frame = tk.Frame(self.register_window)
        self.confirm_password_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.confirm_password_label = tk.Label(self.confirm_password_frame, text="Nhập lại mật khẩu:  ", borderwidth=0)
        self.confirm_password_label.pack(side=tk.LEFT, padx=(13, 0))

        self.confirm_password_entry = tk.Entry(self.confirm_password_frame, width=30)
        self.confirm_password_entry.pack(side=tk.LEFT, padx=(0, 13))

        self.function_frame = tk.Frame(self.register_window)
        self.function_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_submit = tk.Button(self.function_frame, text="Đăng kí", command=self.submit_registration)
        self.button_submit.pack(side=tk.RIGHT, padx=(0, 20))

    def submit_registration(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if username == "" or password == "" or confirm_password == "":
            messagebox.showerror("Lỗi", "Không được để trống các trường", parent=self.register_window)
            return

        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu không khớp", parent=self.register_window)
            return
        else:
            credentials = {
                "username": username,
                "password": password
            }

            response = requests.post("http://127.0.0.1:8000/register", json=credentials)

            if response.json()["result"] == "success":
                messagebox.showinfo("Kết quả", response.json()["message"], parent=self.register_window)
                self.register_window.destroy()
            else:
                messagebox.showerror("Lỗi", response.json()["message"], parent=self.register_window)
