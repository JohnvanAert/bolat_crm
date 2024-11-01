import tkinter as tk
from tkinter import messagebox
from database import get_cabins, update_cabin, add_cabin  # Предполагаем функции для работы с БД

def create_cabin_page(root):
    frame = tk.Frame(root)

    tk.Label(frame, text="Имя кабинки").grid(row=0, column=0)
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)

    tk.Label(frame, text="Цена кабинки").grid(row=1, column=0)
    entry_price = tk.Entry(frame)
    entry_price.grid(row=1, column=1)

    def add_new_cabin():
        name = entry_name.get()
        price = float(entry_price.get())
        try:
            add_cabin(name, price)
            messagebox.showinfo("Успех", "Кабинка добавлена!")
            display_cabins()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить кабинку: {e}")

    def update_cabin_price():
        selected_cabin_id = cabin_combo.get()
        new_price = float(entry_price.get())
        try:
            update_cabin(selected_cabin_id, new_price)
            messagebox.showinfo("Успех", "Цена кабинки обновлена!")
            display_cabins()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить цену: {e}")

    tk.Button(frame, text="Добавить кабинку", command=add_new_cabin).grid(row=2, column=0, columnspan=2)
    tk.Button(frame, text="Обновить цену", command=update_cabin_price).grid(row=3, column=0, columnspan=2)

    # ComboBox для выбора кабинки
    cabin_combo = tk.StringVar()
    tk.Label(frame, text="Выберите кабинку").grid(row=4, column=0)
    cabins_combo = tk.Combobox(frame, textvariable=cabin_combo)
    cabins_combo.grid(row=4, column=1)

    def display_cabins():
        cabins = get_cabins()
        cabins_combo['values'] = [f"{cabin['id']} - {cabin['name']}" for cabin in cabins]

    display_cabins()

    return frame
