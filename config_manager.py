import os
import json
import shutil
import ttkbootstrap as tb

class ConfigManager:
    CONFIG_FILE = "config.json"
    SESSION_FILE = "session.json"

    @classmethod
    def load(cls, key, default=None):
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, "r") as f:
                return json.load(f).get(key, default)
        return default

    @classmethod
    def save(cls, key, value):
        data = {}
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, "r") as f:
                data = json.load(f)
        data[key] = value
        with open(cls.CONFIG_FILE, "w") as f:
            json.dump(data, f)

    @classmethod
    def load_theme(cls):
        return cls.load("theme", "flatly")

    @classmethod
    def save_theme(cls, theme_name):
        cls.save("theme", theme_name)

    @classmethod
    def load_session(cls):
        if os.path.exists(cls.SESSION_FILE):
            with open(cls.SESSION_FILE, "r") as f:
                return json.load(f).get("current_user")
        return None

    @classmethod
    def save_session(cls, user):
        with open(cls.SESSION_FILE, "w") as f:
            json.dump({"current_user": user}, f)

    @classmethod
    def clear_cache(cls):
        cache_dirs = ["cache", "__pycache__"]
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    os.makedirs(cache_dir)
                except Exception as e:
                    print(f"Ошибка очистки {cache_dir}: {e}")
        tb.Messagebox.show_info("Кэш очищен", "Кэш успешно удален!")
