import tkinter as tk
from tkinter import messagebox, ttk
from database import get_cabins, update_cabin, add_cabin, delete_cabin, has_sales_records
from cabin_data import add_observer, update_cabins_data, get_cabins_data

def create_cabin_page(root):
    frame = tk.Frame(root)
    tk.Label(frame, text="Управление кабинками", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)
    rows_per_page = 10  # Количество строк на странице
    current_page = 1  # Текущая страница

    def validate_only_numbers(event):
            """Разрешает вводить только цифры."""
            entry = event.widget
            value = entry.get()
            if not value.isdigit():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isdigit, value)))

    # Поля для добавления новой кабинки
    tk.Label(frame, text="Имя новой кабинки").grid(row=1, column=0)
    entry_new_name = ttk.Entry(frame)
    entry_new_name.grid(row=1, column=1, pady=10)

    tk.Label(frame, text="Цена новой кабинки").grid(row=2, column=0)
    entry_new_price = ttk.Entry(frame)
    entry_new_price.grid(row=2, column=1, pady=10)
    entry_new_price.bind("<KeyRelease>", validate_only_numbers)
                            
    tk.Label(frame, text="Вместимость").grid(row=3, column=0)
    entry_new_capacity = ttk.Entry(frame)
    entry_new_capacity.grid(row=3, column=1, pady=10)
    entry_new_capacity.bind("<KeyRelease>", validate_only_numbers)
    
    # Функция для добавления новой кабинки
    def add_new_cabin():
        name = entry_new_name.get()
        price = entry_new_price.get()
        capacity = entry_new_capacity.get()

        if not name or not price:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        try:
            price = float(price)
            capacity = int(capacity)
            if capacity <= 0:
                messagebox.showerror("Ошибка", "Вместимость должна быть положительным числом!")
                return

            add_cabin(name, price, capacity)
            messagebox.showinfo("Успех", "Кабинка добавлена!")
            entry_new_name.delete(0, tk.END)
            entry_new_price.delete(0, tk.END)
            entry_new_capacity.delete(0, tk.END)
            load_and_update_cabins()  # Обновить данные кабинок
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить кабинку: {e}")

    add_button = ttk.Button(frame, text="Добавить кабинку", command=add_new_cabin)
    add_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Таблица для отображения кабинок
    columns = ('ID', 'Имя кабинки', 'Цена кабинки', 'Вместимость')
    cabin_table = ttk.Treeview(frame, columns=columns, show='headings')
    for col in columns:
        cabin_table.heading(col, text=col)
    cabin_table.grid(row=5, column=0, columnspan=3, pady=10)

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
            cabin_table.insert('', 'end', values=(cabin['id'], cabin['name'], cabin['price'], cabin['capacity']))

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
    pagination_frame.grid(row=6, column=0, columnspan=3)

    prev_button = ttk.Button(pagination_frame, text="Предыдущая", command=prev_page)
    prev_button.pack(side='left')

    pagination_label = tk.Label(pagination_frame, text="Страница 1")
    pagination_label.pack(side='left')

    next_button = ttk.Button(pagination_frame, text="Следующая", command=next_page)
    next_button.pack(side='left')

    # Функция для редактирования и удаления кабинки в модальном окне
    def open_edit_modal(cabin_id, current_name, current_price, current_capacity):
        modal_window = tk.Toplevel(frame)
        modal_window.title("Редактировать/Удалить кабинку")
        
        def validate_only_letters(event):
            """Разрешает вводить только буквы и пробелы."""
            entry = event.widget
            value = entry.get()
            # Фильтруем строку: оставляем только буквы и пробелы
            filtered_value = ''.join(char for char in value if char.isalpha() or char.isspace())
            
            if value != filtered_value:
                entry.delete(0, tk.END)
                entry.insert(0, filtered_value)
        def validate_only_numbers(event):
            """Разрешает вводить только цифры."""
            entry = event.widget
            value = entry.get()
            if not value.isdigit():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isdigit, value)))

        tk.Label(modal_window, text="Имя кабинки").grid(row=0, column=0)
        name_var = tk.StringVar(value=current_name)
        entry_name = ttk.Entry(modal_window, textvariable=name_var)
        entry_name.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(modal_window, text="Цена кабинки").grid(row=1, column=0)
        price_var = tk.StringVar(value=current_price)
        entry_price = ttk.Entry(modal_window, textvariable=price_var)
        entry_price.grid(row=1, column=1, pady=10)
        entry_price.bind("<KeyRelease>", validate_only_numbers)
        # Поле для вместимости
        tk.Label(modal_window, text="Вместимость").grid(row=2, column=0)
        capacity_var = tk.StringVar(value=current_capacity)
        entry_capacity = ttk.Entry(modal_window, textvariable=capacity_var)
        entry_capacity.grid(row=2, column=1, pady=10)
        entry_capacity.bind("<KeyRelease>", validate_only_numbers)
        def save_changes():
            new_name = name_var.get()
            new_price = price_var.get()
            new_capacity = capacity_var.get()
            if not new_name or not new_price or not new_capacity:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            try:
                new_price = float(new_price)
                new_capacity = int(new_capacity)
                update_cabin(cabin_id, new_name, new_price, new_capacity)
                messagebox.showinfo("Успех", "Кабинка обновлена!")
                modal_window.destroy()
                load_and_update_cabins()
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить кабинку: {e}")

        def delete_cabin_action(cabin_id):
            if has_sales_records(cabin_id):
                messagebox.showwarning("Предупреждение", "У данной кабинки есть записи в продажах. Удаление невозможно.")
                return
            
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить кабинку?"):
                try:
                    delete_cabin(cabin_id)
                    messagebox.showinfo("Успех", "Кабинка удалена!")
                    modal_window.destroy()
                    load_and_update_cabins()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить кабинку: {e}")

        save_button = ttk.Button(modal_window, text="Сохранить", command=save_changes)
        save_button.grid(row=3, column=0, columnspan=2, pady=5)

        delete_button = ttk.Button(modal_window, text="Удалить", command=lambda:delete_cabin_action(cabin_id))
        delete_button.grid(row=4, column=0, columnspan=2, pady=5)

    # Обработчик двойного клика по таблице
    def on_table_double_click(event):
        item_id = cabin_table.focus()
        if not item_id:
            return

        cabin_data = cabin_table.item(item_id, 'values')
        cabin_id, name, price, capacity = cabin_data
        open_edit_modal(cabin_id, name, price, capacity)

    cabin_table.bind('<Double-1>', on_table_double_click)

    def auto_refresh():
        load_and_update_cabins()
        frame.after(300000, auto_refresh)  # 300000 миллисекунд = 5 минут
    # Регистрация функции отображения как наблюдателя
    add_observer(display_cabins)
    auto_refresh()
    # Первоначальная загрузка данных кабинок
    load_and_update_cabins()

    return frame
