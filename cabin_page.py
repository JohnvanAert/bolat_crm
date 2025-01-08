import tkinter as tk
from tkinter import messagebox, ttk
from database import get_cabins, update_cabin, add_cabin, delete_cabin
from cabin_data import add_observer, update_cabins_data, get_cabins_data

def create_cabin_page(root):
    frame = tk.Frame(root)
    rows_per_page = 10  # Количество строк на странице
    current_page = 1  # Текущая страница

    # Поля для добавления новой кабинки
    tk.Label(frame, text="Имя новой кабинки").grid(row=0, column=0)
    entry_new_name = tk.Entry(frame)
    entry_new_name.grid(row=0, column=1)

    tk.Label(frame, text="Цена новой кабинки").grid(row=1, column=0)
    entry_new_price = tk.Entry(frame)
    entry_new_price.grid(row=1, column=1)

    # Функция для добавления новой кабинки
    def add_new_cabin():
        name = entry_new_name.get()
        price = entry_new_price.get()

        if not name or not price:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        try:
            price = float(price)
            add_cabin(name, price)
            messagebox.showinfo("Успех", "Кабинка добавлена!")
            entry_new_name.delete(0, tk.END)
            entry_new_price.delete(0, tk.END)
            load_and_update_cabins()  # Обновить данные кабинок
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить кабинку: {e}")

    add_button = tk.Button(frame, text="Добавить кабинку", command=add_new_cabin)
    add_button.grid(row=2, column=0, columnspan=2)

    # Таблица для отображения кабинок
    columns = ('ID', 'Имя кабинки', 'Цена кабинки')
    cabin_table = ttk.Treeview(frame, columns=columns, show='headings')
    for col in columns:
        cabin_table.heading(col, text=col)
    cabin_table.grid(row=3, column=0, columnspan=3, pady=10)

    # Функция для загрузки и обновления данных кабинок
    def load_and_update_cabins():
        cabins = get_cabins()
        update_cabins_data(cabins)
        display_cabins()

    # Функция для отображения кабинок с учетом пагинации
    def display_cabins():
        nonlocal current_page
        for row in cabin_table.get_children():
            cabin_table.delete(row)

        cabins = get_cabins_data()
        total_pages = (len(cabins) + rows_per_page - 1) // rows_per_page  # Рассчитать количество страниц

        start_index = (current_page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        for cabin in cabins[start_index:end_index]:
            cabin_table.insert('', 'end', values=(cabin['id'], cabin['name'], cabin['price']))

        # Обновить статус пагинации
        pagination_label.config(text=f"Страница {current_page} из {total_pages}")
        prev_button.config(state='normal' if current_page > 1 else 'disabled')
        next_button.config(state='normal' if current_page < total_pages else 'disabled')

    # Функции для управления переходами между страницами
    def next_page():
        nonlocal current_page
        current_page += 1
        display_cabins()

    def prev_page():
        nonlocal current_page
        current_page -= 1
        display_cabins()

    # Кнопки управления пагинацией
    pagination_frame = tk.Frame(frame)
    pagination_frame.grid(row=4, column=0, columnspan=3)

    prev_button = tk.Button(pagination_frame, text="Предыдущая", command=prev_page)
    prev_button.pack(side='left')

    pagination_label = tk.Label(pagination_frame, text="Страница 1")
    pagination_label.pack(side='left')

    next_button = tk.Button(pagination_frame, text="Следующая", command=next_page)
    next_button.pack(side='left')

    # Функция для редактирования и удаления кабинки в модальном окне
    def open_edit_modal(cabin_id, current_name, current_price):
        modal_window = tk.Toplevel(frame)
        modal_window.title("Редактировать/Удалить кабинку")
        
        def validate_only_letters(event):
            """Разрешает вводить только буквы."""
            entry = event.widget
            value = entry.get()
            if not value.isalpha():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isalpha, value)))

        def validate_only_numbers(event):
            """Разрешает вводить только цифры."""
            entry = event.widget
            value = entry.get()
            if not value.isdigit():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isdigit, value)))

        tk.Label(modal_window, text="Имя кабинки").grid(row=0, column=0)
        name_var = tk.StringVar(value=current_name)
        entry_name = tk.Entry(modal_window, textvariable=name_var)
        entry_name.grid(row=0, column=1)

        tk.Label(modal_window, text="Цена кабинки").grid(row=1, column=0)
        price_var = tk.StringVar(value=current_price)
        entry_price = tk.Entry(modal_window, textvariable=price_var)
        entry_price.grid(row=1, column=1)
        entry_price.bind("<KeyRelease>", validate_only_numbers)

        def save_changes():
            new_name = name_var.get()
            new_price = price_var.get()

            if not new_name or not new_price:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            try:
                new_price = float(new_price)
                update_cabin(cabin_id, new_name, new_price)
                messagebox.showinfo("Успех", "Кабинка обновлена!")
                modal_window.destroy()
                load_and_update_cabins()
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить кабинку: {e}")

        def delete_cabin_action():
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить кабинку?"):
                try:
                    delete_cabin(cabin_id)
                    messagebox.showinfo("Успех", "Кабинка удалена!")
                    modal_window.destroy()
                    load_and_update_cabins()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить кабинку: {e}")

        save_button = tk.Button(modal_window, text="Сохранить", command=save_changes)
        save_button.grid(row=2, column=0, columnspan=2)

        delete_button = tk.Button(modal_window, text="Удалить", command=delete_cabin_action)
        delete_button.grid(row=3, column=0, columnspan=2)

    # Обработчик двойного клика по таблице
    def on_table_double_click(event):
        item_id = cabin_table.focus()
        if not item_id:
            return

        cabin_data = cabin_table.item(item_id, 'values')
        cabin_id, name, price = cabin_data
        open_edit_modal(cabin_id, name, price)

    cabin_table.bind('<Double-1>', on_table_double_click)

    # Регистрация функции отображения как наблюдателя
    add_observer(display_cabins)

    # Первоначальная загрузка данных кабинок
    load_and_update_cabins()

    return frame
