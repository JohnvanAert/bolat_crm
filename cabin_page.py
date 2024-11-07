import tkinter as tk
from tkinter import messagebox, ttk
from database import get_cabins, update_cabin, add_cabin, delete_cabin
from cabin_data import add_observer, update_cabins_data, get_cabins_data

def create_cabin_page(root):
    frame = tk.Frame(root)

    # Fields to add a new cabin
    tk.Label(frame, text="Имя новой кабинки").grid(row=0, column=0)
    entry_new_name = tk.Entry(frame)
    entry_new_name.grid(row=0, column=1)

    tk.Label(frame, text="Цена новой кабинки").grid(row=1, column=0)
    entry_new_price = tk.Entry(frame)
    entry_new_price.grid(row=1, column=1)

    # Function to add a new cabin
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
            load_and_update_cabins()  # Update the cabin data and notify observers
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить кабинку: {e}")

    add_button = tk.Button(frame, text="Добавить кабинку", command=add_new_cabin)
    add_button.grid(row=2, column=0, columnspan=2)

    # Table to display and edit cabins
    columns = ('ID', 'Имя кабинки', 'Цена кабинки', 'Редактировать', 'Удалить')
    cabin_table = ttk.Treeview(frame, columns=columns, show='headings')
    for col in columns:
        cabin_table.heading(col, text=col)
    cabin_table.grid(row=3, column=0, columnspan=3, pady=10)

    # Function to load data and update cabins
    def load_and_update_cabins():
        cabins = get_cabins()
        update_cabins_data(cabins)

    # Display cabins
    def display_cabins():
        for row in cabin_table.get_children():
            cabin_table.delete(row)
        for cabin in get_cabins_data():
            cabin_table.insert('', 'end', values=(cabin['id'], cabin['name'], cabin['price'], 'Редактировать', 'Удалить'))

    # Function to edit a cabin
    def edit_cabin(cabin_id, current_name, current_price):
        edit_window = tk.Toplevel(frame)
        edit_window.title("Редактировать кабинку")

        tk.Label(edit_window, text="Имя кабинки").grid(row=0, column=0)
        name_var = tk.StringVar(value=current_name)
        entry_name = tk.Entry(edit_window, textvariable=name_var)
        entry_name.grid(row=0, column=1)

        tk.Label(edit_window, text="Цена кабинки").grid(row=1, column=0)
        price_var = tk.StringVar(value=current_price)
        entry_price = tk.Entry(edit_window, textvariable=price_var)
        entry_price.grid(row=1, column=1)

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
                edit_window.destroy()
                load_and_update_cabins()  # Update the cabin data and notify observers
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить кабинку: {e}")

        save_button = tk.Button(edit_window, text="Сохранить", command=save_changes)
        save_button.grid(row=2, column=0, columnspan=2)

    # Function to delete a cabin
    def delete_cabin_entry(cabin_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить кабинку?"):
            try:
                delete_cabin(cabin_id)
                messagebox.showinfo("Успех", "Кабинка удалена!")
                load_and_update_cabins()  # Update the cabin data and notify observers
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить кабинку: {e}")

    # Handle table button clicks
    def on_table_click(event):
        item_id = cabin_table.focus()
        if not item_id:
            return

        cabin_data = cabin_table.item(item_id, 'values')
        cabin_id, name, price, action_edit, action_delete = cabin_data

        column = cabin_table.identify_column(event.x)
        if column == '#4':  # Edit column
            edit_cabin(cabin_id, name, price)
        elif column == '#5':  # Delete column
            delete_cabin_entry(cabin_id)

    cabin_table.bind('<Button-1>', on_table_click)

    # Register the display function as an observer
    add_observer(display_cabins)

    # Initial load of cabin data
    load_and_update_cabins()

    return frame
