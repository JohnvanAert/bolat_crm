import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from database import insert_sales_data, fetch_sales_data, get_cabins, update_sales_data
from cabin_data import add_observer, get_cabins_data

def create_gui_page(root):
    frame = tk.Frame(root)

    tk.Label(frame, text="Имя").grid(row=2, column=0)
    entry_name = tk.Entry(frame)
    entry_name.grid(row=2, column=1)
    
    tk.Label(frame, text="Номер").grid(row=3, column=0)
    entry_number = tk.Entry(frame)
    entry_number.grid(row=3, column=1)

    selected_cabin_id = tk.StringVar()
    tk.Label(frame, text="Выберите кабинку").grid(row=0, column=0)
    cabins_combo = ttk.Combobox(frame, textvariable=selected_cabin_id, state="readonly")
    cabins_combo.grid(row=0, column=1)

    tk.Label(frame, text="Общая продажа").grid(row=1, column=0)
    entry_sales = tk.Entry(frame, state='readonly')
    entry_sales.grid(row=1, column=1)

    def update_cabins_combo():
        cabins_data = get_cabins_data()
        cabins_combo_values = [f"{cabin['name']} - {cabin['price']} $" for cabin in cabins_data]
        cabins_combo['values'] = cabins_combo_values

    update_cabins_combo()
    add_observer(update_cabins_combo)

    def update_sales_price(event):
        selected = cabins_combo.get().split(" - ")[0]
        cabins_data = get_cabins_data()
        for cabin in cabins_data:
            if cabin['name'] == selected:
                entry_sales.config(state='normal')
                entry_sales.delete(0, tk.END)
                entry_sales.insert(0, cabin['price'])
                entry_sales.config(state='readonly')
                break

    cabins_combo.bind("<<ComboboxSelected>>", update_sales_price)

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
            display_sales_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    tk.Button(frame, text="Добавить", command=submit_data).grid(row=4, columnspan=2)

    tree = ttk.Treeview(frame, columns=("id", "name", "number", "cabins_count", "total_sales", "date"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("cabins_count", text="Выбранная кабинка")
    tree.heading("total_sales", text="Общая продажа")
    tree.heading("name", text="Имя")
    tree.heading("number", text="Номер")
    tree.heading("date", text="Дата и Время")
    tree.grid(row=5, column=0, columnspan=2)

    def display_sales_data():
        for item in tree.get_children():
            tree.delete(item)
        for row in fetch_sales_data():
            tree.insert("", tk.END, values=row)
        update_cabins_combo()

    def on_item_double_click(event):
        item = tree.selection()[0]
        selected_data = tree.item(item, "values")

        edit_window = tk.Toplevel(root)
        edit_window.title("Редактирование заказа")

        tk.Label(edit_window, text="Имя").grid(row=0, column=0)
        edit_name_entry = tk.Entry(edit_window)
        edit_name_entry.grid(row=0, column=1)
        edit_name_entry.insert(0, selected_data[1])

        tk.Label(edit_window, text="Номер").grid(row=1, column=0)
        edit_number_entry = tk.Entry(edit_window)
        edit_number_entry.grid(row=1, column=1)
        edit_number_entry.insert(0, selected_data[2])

        tk.Label(edit_window, text="Выберите кабинку").grid(row=2, column=0)
        edit_cabins_combo = ttk.Combobox(edit_window, state="readonly")
        edit_cabins_combo.grid(row=2, column=1)
        edit_cabins_combo['values'] = cabins_combo['values']
        edit_cabins_combo.set(selected_data[3])

        def save_changes():
            new_name = edit_name_entry.get()
            new_number = edit_number_entry.get()
            new_cabin = edit_cabins_combo.get().split(" - ")[0]
            selected_cabin_id = next((cabin['id'] for cabin in get_cabins_data() if cabin['name'] == new_cabin), None)
            cabin_price = next((cabin['price'] for cabin in get_cabins_data() if cabin['name'] == new_cabin), None)

            update_sales_data(selected_data[0], new_name, new_number, selected_cabin_id, cabin_price)
            messagebox.showinfo("Успех", "Данные успешно обновлены!")
            display_sales_data()
            edit_window.destroy()

        tk.Button(edit_window, text="Сохранить", command=save_changes).grid(row=3, columnspan=2)

    tree.bind("<Double-1>", on_item_double_click)
    display_sales_data()
    return frame
