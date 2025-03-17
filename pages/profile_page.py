import tkinter as tk
import ttkbootstrap as tb
from auth import get_user_details

def create_profile_page(parent, user_id):
    frame = tb.Frame(parent)
    
    # Заголовок
    tb.Label(frame, text="Профиль пользователя", font=("Helvetica", 18, "bold")).pack(pady=20)
    
    # Получаем данные пользователя
    user_data = get_user_details(user_id)
    
    # Контейнер для информации
    info_frame = tb.Frame(frame)
    info_frame.pack(pady=10, padx=20, fill="x")
    
    # Отображение информации
    fields = [
        ("Логин:", "username"),
        ("Роль:", "role"),
        ("Дата регистрации:", "created_at")
    ]
    
    for label_text, field in fields:
        row = tb.Frame(info_frame)
        row.pack(fill="x", pady=5)
        
        tb.Label(row, text=label_text, width=15, anchor="w").pack(side="left")
        tb.Label(row, text=user_data.get(field, "N/A"), width=25, anchor="w").pack(side="left")
    
    # Кнопка смены пароля
    tb.Button(frame, 
             text="Сменить пароль", 
             bootstyle="warning",
             command=lambda: show_change_password_dialog(parent, user_id)).pack(pady=20)
    
    return frame

def show_change_password_dialog(parent):
    dialog = tb.Toplevel(parent)
    dialog.title("Смена пароля")
    dialog.geometry("300x200")
    
    new_password_var = tb.StringVar()
    confirm_password_var = tb.StringVar()
    
    tb.Label(dialog, text="Новый пароль:").pack(pady=5)
    tb.Entry(dialog, textvariable=new_password_var, show="*").pack(pady=5)
    
    tb.Label(dialog, text="Подтвердите пароль:").pack(pady=5)
    tb.Entry(dialog, textvariable=confirm_password_var, show="*").pack(pady=5)
    
    def change_password():
        if new_password_var.get() != confirm_password_var.get():
            tb.dialogs.Messagebox.show_error("Пароли не совпадают")
            return
        
        # Здесь должна быть логика обновления пароля
        tb.dialogs.Messagebox.show_info("Успех", "Пароль успешно изменен")
        dialog.destroy()
    
    tb.Button(dialog, text="Изменить", command=change_password).pack(pady=10)
