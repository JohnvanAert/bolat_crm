import tkinter as tk
from tkinter import messagebox, ttk
from database import insert_sales_data, fetch_sales_data, get_cabins
from cabin_data import add_observer, get_cabins_data

def create_gui_page(root):
    frame = tk.Frame(root)

    tk.Label(frame, text="Имя").grid(row=2, column=0)
    entry_name = tk.Entry(frame)
    entry_name.grid(row=2, column=1)
    
    tk.Label(frame, text="Номер").grid(row=3, column=0)
    entry_number = tk.Entry(frame)
    entry_number.grid(row=3, column=1)

    # Создаем комбобокс для выбора кабины
    selected_cabin_id = tk.StringVar()
    tk.Label(frame, text="Выберите кабинку").grid(row=0, column=0)
    cabins_combo = ttk.Combobox(frame, textvariable=selected_cabin_id, state="readonly")
    cabins_combo.grid(row=0, column=1)

    # Поле "Общая продажа" обновляется автоматически
    tk.Label(frame, text="Общая продажа").grid(row=1, column=0)
    entry_sales = tk.Entry(frame, state='readonly')
    entry_sales.grid(row=1, column=1)

    # Функция для обновления выпадающего списка кабинок
    def update_cabins_combo():
        cabins_data = get_cabins_data()  # Получаем актуальные данные по кабинкам
        cabins_combo_values = [f"{cabin['name']} - {cabin['price']} $" for cabin in cabins_data]
        cabins_combo['values'] = cabins_combo_values  # Обновляем значения комбобокса

    # Изначально загружаем данные кабинок
    update_cabins_combo()

    # Подписываем update_cabins_combo на обновления данных о кабинках
    add_observer(update_cabins_combo)

    # Обновление значения "Общая продажа" при выборе кабинки
    def update_sales_price(event):
        selected = cabins_combo.get().split(" - ")[0]  # Получаем название кабинки
        cabins_data = get_cabins_data()
        for cabin in cabins_data:
            if cabin['name'] == selected:
                entry_sales.config(state='normal')
                entry_sales.delete(0, tk.END)
                entry_sales.insert(0, cabin['price'])
                entry_sales.config(state='readonly')
                break

    cabins_combo.bind("<<ComboboxSelected>>", update_sales_price)

    # Функция для отправки данных в базу
    def submit_data():
        try:
            name = entry_name.get()
            number = entry_number.get()
            selected_cabin = cabins_combo.get().split(" - ")[0]
            cabins_data = get_cabins_data()
            selected_cabin_id = next((cabin['id'] for cabin in cabins_data if cabin['name'] == selected_cabin), None)
            cabin_price = next((cabin['price'] for cabin in cabins_data if cabin['name'] == selected_cabin), None)

            insert_sales_data(name, number, selected_cabin_id, cabin_price)
            messagebox.showinfo("Успех", "Данные успешно добавлены!")
            display_sales_data()  # Обновляем данные в таблице и комбобоксе
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    tk.Button(frame, text="Добавить", command=submit_data).grid(row=4, columnspan=2)
    
    # Таблица для отображения данных
    tree = ttk.Treeview(frame, columns=("id", "name", "number", "cabins_count", "total_sales", "date"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("cabins_count", text="Выбранная кабинка")
    tree.heading("total_sales", text="Общая продажа")
    tree.heading("name", text="Имя")
    tree.heading("number", text="Номер")
    tree.heading("date", text="Дата и Время")
    tree.grid(row=5, column=0, columnspan=2)

    # Функция для отображения данных в таблице
    def display_sales_data():
        # Очищаем таблицу
        for item in tree.get_children():
            tree.delete(item)
        
        # Загружаем и отображаем актуальные данные о продажах
        for row in fetch_sales_data():
            tree.insert("", tk.END, values=row)
        
        # Обновляем список кабинок
        update_cabins_combo()

    display_sales_data()
    return frame
