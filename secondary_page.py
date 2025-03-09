import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import Button, Frame, Label
from auth import get_users, update_user, create_user, delete_user
import ttkbootstrap as tb
import bcrypt
from auth import get_user_details

def create_secondary_page(root, user_id):
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)
    user_data = get_user_details(user_id)

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

    # Открытие модального окна редактирования
    def open_edit_user_window(user_id, username, role):
        modal = tk.Toplevel()
        modal.title("Редактировать пользователя")
        modal.geometry("300x200")
        modal.transient()
        modal.grab_set()

        tk.Label(modal, text="Имя пользователя").pack(pady=5)
        new_username = tk.StringVar(value=username)
        new_username_entry = tk.Entry(modal, textvariable=new_username)
        new_username_entry.pack()

        tk.Label(modal, text="Роль").pack(pady=5)
        new_user_role = tk.StringVar(value=role)
        new_role_combobox = ttk.Combobox(modal, textvariable=new_user_role, values=["admin", "user"], state="readonly")
        new_role_combobox.pack()

        def save_changes():
            updated_name = new_username.get().strip()
            updated_role = new_user_role.get().strip()

            if not updated_name or not updated_role:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены!", parent=modal)
                return

            update_user(user_id, updated_name, updated_role)
            load_users()
            messagebox.showinfo("Успех", "Данные пользователя обновлены!", parent=modal)
            modal.destroy()

        def delete_current_user():
            confirm = messagebox.askyesno("Удаление", f"Вы уверены, что хотите удалить {username}?", parent=modal)
            if confirm:
                delete_user(user_id)
                load_users()
                messagebox.showinfo("Удалено", f"Пользователь {username} удален!", parent=modal)
                modal.destroy()
   

        ttk.Button(modal, text="Сохранить", command=save_changes).pack(pady=10)
        ttk.Button(modal, text="Удалить пользователя", command=delete_current_user, bootstyle="danger").pack(pady=5)

    # Обработчик двойного клика по таблице
    def on_double_click(event):
        selected = user_table.selection()
        if selected:
            values = user_table.item(selected[0], "values")
            user_id, username, role = values
            open_edit_user_window(user_id, username, role)

    user_table.bind("<Double-1>", on_double_click)

    ttk.Button(main_area, text="Добавить пользователя", command=lambda: open_add_user_window(load_users)).pack(pady=10)

    def open_add_user_window(load_users_callback):
        modal = tk.Toplevel()
        modal.title("Добавить пользователя")
        modal.geometry("300x250")
        modal.transient()  # Сделать окно модальным

        tk.Label(modal, text="Имя пользователя").pack(pady=5)
        new_username = tk.StringVar()
        new_username_entry = tk.Entry(modal, textvariable=new_username)
        new_username_entry.pack()

        tk.Label(modal, text="Пароль").pack(pady=5)
        new_password = tk.StringVar()
        new_password_entry = tk.Entry(modal, textvariable=new_password, show="*")
        new_password_entry.pack()

        tk.Label(modal, text="Роль").pack(pady=5)
        new_user_role = tk.StringVar(value="user")
        new_role_combobox = ttk.Combobox(modal, textvariable=new_user_role, values=["admin", "user"], state="readonly")
        new_role_combobox.pack()

        def create_new_user():
            username = new_username.get().strip()
            password = new_password.get().strip()
            role = new_user_role.get().strip()

            if not username or not password or not role:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены!", parent=modal)
                return

            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            create_user(username, hashed_password, role)
            load_users_callback()
            messagebox.showinfo("Успех", f"Пользователь {username} успешно создан!", parent=modal)
            modal.destroy()

        ttk.Button(modal, text="Создать", command=create_new_user).pack(pady=10)

    return frame
