import tkinter as tk
import ttkbootstrap as tb
from auth import register_user  # Функция для регистрации пользователя

class RegisterWindow(tb.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Регистрация")
        self.geometry("300x250")
        self.resizable(False, False)
        self.on_success = on_success

        self.username_var = tb.StringVar()
        self.password_var = tb.StringVar()
        self.confirm_password_var = tb.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tb.Label(self, text="Логин:").pack(pady=5)
        tb.Entry(self, textvariable=self.username_var).pack(pady=5)

        tb.Label(self, text="Пароль:").pack(pady=5)
        tb.Entry(self, textvariable=self.password_var, show="*").pack(pady=5)

        tb.Label(self, text="Подтвердите пароль:").pack(pady=5)
        tb.Entry(self, textvariable=self.confirm_password_var, show="*").pack(pady=5)

        # Кнопка регистрации
        tb.Button(self, text="Зарегистрироваться", command=self.register).pack(pady=10)

    def register(self):
        username = self.username_var.get()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()

        if not username or not password:
            tb.dialogs.Messagebox.show_error("Заполните все поля!")
            return

        if password != confirm_password:
            tb.dialogs.Messagebox.show_error("Пароли не совпадают!")
            return

        if register_user(username, password):  # Функция добавляет пользователя в БД
            tb.dialogs.Messagebox.show_info("Регистрация успешна!")
            self.on_success()  # Закрываем окно и открываем главное приложение
            self.destroy()
        else:
            tb.dialogs.Messagebox.show_error("Такой пользователь уже существует!")
