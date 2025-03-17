from base_window import BaseWindow
from auth import has_users
from login_window import LoginWindow
from register_window import RegisterWindow
from navigation import NavigationBar
from config_manager import ConfigManager
import tkinter as tk
from pages import (
    MainPage,
    ProductsPage,
    BookingPage,
    CabinPage,
    ExpensesPage,
    StatisticsPage,
    AuthPage,
    ProfilePage
)
import ttkbootstrap as tb

class App(BaseWindow):
    def __init__(self):
        super().__init__()
        self.current_user = ConfigManager.load_session()
        self.pages = {}
        self.page_size = 15
        self._init_ui()
        self._check_first_run()

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.nav_bar = None
        self.settings_button = None
        self._create_navigation()
        self._create_pages()
        self.show_page("main")

    def _check_first_run(self):
        """Проверка первого запуска приложения"""
        if not has_users():
            self._register_admin()

    def _register_admin(self):
        """Регистрация администратора при первом запуске"""
        reg_window = RegisterWindow(
            self,
            on_success=lambda: LoginWindow(self, self.on_login_success)
        )
        self.wait_window(reg_window)

    def init_auth(self):
        """Инициализация авторизации"""
        if not has_users():
            reg_window = RegisterWindow(self, on_success=lambda: LoginWindow(self, self.on_login_success))
            self.wait_window(reg_window)

        login_window = LoginWindow(self, self.on_login_success)
        self.wait_window(login_window)

        if not self.current_user:
            self.destroy()

    def _create_navigation(self):
        """Создание навигационной панели"""
        if self.nav_bar:
            self.nav_bar.destroy()

        self.nav_bar = NavigationBar(
            self,
            show_pages=self._get_page_handlers(),
            logout_handler=self.logout
        )
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)

    def _create_pages(self):
        """Инициализация всех страниц приложения"""
        self.pages = {
            "main": MainPage(self),
            "products": ProductsPage(self),
            "booking": BookingPage(self),
            "cabin": CabinPage(self),
            "expenses": ExpensesPage(self),
            "statistics": StatisticsPage(self),
            "auth": AuthPage(self),
            "profile": ProfilePage(self, self.current_user)
        }
    def on_login_success(self, user):
        """Действия после успешного входа"""
        self.current_user = user
        ConfigManager.save_session(user)
        self.deiconify()
        self.init_navigation()

    def show_page(self, page_name):
        """Переключение между страницами"""
        # Убираем текущие страницы
        for page in self.pages.values():
            page.pack_forget()

        # Создаем страницу, если её нет
        if page_name not in self.pages:
            if page_name == "main":
                self.pages[page_name] = MainPage(self)
            elif page_name == "profile":
                self.pages[page_name] = ProfilePage(self)

        # Показываем нужную страницу
        self.pages[page_name].pack(fill="both", expand=True)

    def logout(self):
        """Выход из системы"""
        ConfigManager.save_session(None)
        self.current_user = None
        self.destroy()
        App().mainloop()

    def _create_settings_button(self):
        """Создает кнопку настроек"""
        self.settings_button = tb.Button(
            self,
            text="Настройки",
            command=self.open_settings,
            bootstyle="primary"
        )
        self.settings_button.place(x=10, y=700)

    def open_settings(self):
        """Открывает окно настроек"""
        settings_window = tb.Toplevel(self)
        settings_window.title("Настройки")
        settings_window.geometry("300x200")
        
        # Добавьте содержимое настроек по необходимости
        tb.Label(settings_window, text="Выберите тему:").pack(pady=10)

