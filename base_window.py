import tkinter as tk
from config_manager import ConfigManager

class BaseWindow(tk.Tk):
    def __init__(self, theme=None):
        theme = theme or ConfigManager.load_theme()
        super().__init__()
        self.configure_theme(theme)
        
    def configure_theme(self, theme):
        self.themename = theme
        self.title("3B CRM")
        self.geometry("1450x800")
        self.minsize(800, 600)
        self.maxsize(1920, 1080)
        self.iconbitmap("icon.ico")