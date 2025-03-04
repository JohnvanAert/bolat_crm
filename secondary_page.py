import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import Button, Frame, Label
from auth import get_users, update_user
import ttkbootstrap as tb

def create_secondary_page(root):
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)

    main_area = tk.Frame(frame)
    main_area.pack(fill='both', expand=True)

    tk.Label(main_area, text="Персонал", font=('Arial', 14)).pack(pady=10)

    # Таблица пользователей
    columns = ("ID", "Имя", "Роль")
    user_table = tb.Treeview(main_area, columns=columns, show="headings")
    for col in columns:
        user_table.heading(col, text=col)
        user_table.column(col, anchor="center")

    user_table.pack(fill="both", expand=True, padx=10, pady=5)

    # Загрузка пользователей из базы
    def load_users():
        users = get_users()  # Получаем пользователей
        user_table.delete(*user_table.get_children())  # Очищаем таблицу
        for user in users:
            user_table.insert("", "end", values=user)

    load_users()  # Заполняем таблицу

    # Форма для редактирования
    tk.Label(main_area, text="Редактировать пользователя").pack(pady=5)

    selected_id = tk.StringVar()
    selected_name = tk.StringVar()
    selected_role = tk.StringVar()

    tk.Label(main_area, text="ID").pack()
    id_entry = tk.Entry(main_area, textvariable=selected_id, state="readonly")
    id_entry.pack()

    tk.Label(main_area, text="Имя").pack()
    name_entry = tk.Entry(main_area, textvariable=selected_name)
    name_entry.pack()

    tk.Label(main_area, text="Роль").pack()
    role_entry = tk.Entry(main_area, textvariable=selected_role)
    role_entry.pack()

    def select_user(event):
        selected = user_table.selection()
        if selected:
            values = user_table.item(selected[0], "values")
            selected_id.set(values[0])
            selected_name.set(values[1])
            selected_role.set(values[2])

    user_table.bind("<<TreeviewSelect>>", select_user)

    def save_changes():
        user_id = selected_id.get()
        new_name = selected_name.get()
        new_role = selected_role.get()
        if user_id and new_name and new_role:
            update_user(user_id, new_name, new_role)
            load_users()

    ttk.Button(main_area, text="Сохранить изменения", command=save_changes).pack(pady=10)

    return frame
