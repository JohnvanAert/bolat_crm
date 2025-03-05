import tkinter as tk
import ttkbootstrap as tb
from auth import authenticate

class LoginWindow(tb.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Авторизация")
        self.geometry("300x200")
        self.resizable(False, False)
        self.on_success = on_success
        
        self.username_var = tb.StringVar()
        self.password_var = tb.StringVar()
        
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tb.Label(self, text="Логин:").pack(pady=5)
        tb.Entry(self, textvariable=self.username_var).pack(pady=5)
        
        tb.Label(self, text="Пароль:").pack(pady=5)
        tb.Entry(self, textvariable=self.password_var, show="*").pack(pady=5)
        
        # Кнопка входа
        tb.Button(self, text="Войти", command=self.login).pack(pady=10)

    def login(self):
        user_id = authenticate(self.username_var.get(), self.password_var.get())
        if user_id:
            self.on_success(user_id)  # Передаем ID
            self.destroy()
        else:
            tb.dialogs.Messagebox.show_error("Неверный логин или пароль")