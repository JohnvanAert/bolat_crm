# navigation.py
import tkinter as tk
import ttkbootstrap as tb
from auth import get_user_details

class NavigationBar(tb.Frame):
    def __init__(self, master, show_pages, logout_handler):
        super().__init__(master)
        self.master = master
        self.show_pages = show_pages
        self.logout_handler = logout_handler
        self.user_role = None
        self.build()

    def build(self):
        self.pack(side=tk.TOP, fill=tk.X)
        self._create_buttons()
        self._create_profile_menu()

    def _create_buttons(self):
        user_data = get_user_details(self.master.current_user)
        self.user_role = user_data.get("role")

        # Основные кнопки
        tb.Button(self, text="Главная", command=self.show_pages["main"]).pack(side=tk.LEFT, padx=5)
        tb.Button(self, text="Бронирование", command=self.show_pages["booking"]).pack(side=tk.LEFT, padx=5)
        tb.Button(self, text="Страница заказов", command=self.show_pages["gui"]).pack(side=tk.LEFT, padx=5)

        # Кнопки для администратора
        if self.user_role == "admin":
            self._add_admin_buttons()

        # Кнопка профиля
        self.profile_button = tb.Button(self, text="Профиль")
        self.profile_button.pack(side=tk.RIGHT, padx=20)

    def _add_admin_buttons(self):
        admin_buttons = [
            ("Склад продуктов", "products"),
            ("Кабинки", "cabin"),
            ("Расходы", "expenses"),
            ("Статистика", "statistics"),
            ("Персонал", "auth")
        ]
        for text, page_key in admin_buttons:
            tb.Button(self, text=text, command=self.show_pages[page_key]).pack(side=tk.LEFT, padx=5)

    def _create_profile_menu(self):
        self.profile_menu = tk.Menu(self, tearoff=0)
        self.profile_menu.add_command(label="Кабинет", command=self.show_pages["profile"])
        self.profile_menu.add_separator()
        self.profile_menu.add_command(label="Выйти", command=self.logout_handler)

        # Привязка событий
        self.profile_button.bind("<Enter>", self._show_menu)
        self.profile_button.bind("<Leave>", self._hide_menu)
        self.profile_button.bind("<Button-1>", self._show_menu)

    def _show_menu(self, event):
        self.profile_menu.post(
            event.widget.winfo_rootx(),
            event.widget.winfo_rooty() + event.widget.winfo_height()
        )

    def _hide_menu(self, event):
        self.profile_menu.unpost()

    def destroy(self):
        self.profile_menu.destroy()
        super().destroy()