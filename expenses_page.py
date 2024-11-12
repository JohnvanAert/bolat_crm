import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from database import fetch_expenses_data, add_expense, update_expense
from expenses_data import add_observer, update_expenses_data, get_expenses_data
from datetime import datetime

def create_expenses_page(root):
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)

    # Search fields
    tk.Label(frame, text="Поиск по имени").pack()
    search_name_entry = tk.Entry(frame)
    search_name_entry.pack()

    tk.Label(frame, text="Поиск по номеру").pack()
    search_price_entry = tk.Entry(frame)
    search_price_entry.pack()

    tk.Label(frame, text="Дата с").pack()
    start_date_entry = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    start_date_entry.pack()

    tk.Label(frame, text="Дата по").pack()
    end_date_entry = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    end_date_entry.pack()

    # Table for displaying expense data
    tree = ttk.Treeview(frame, columns=("id", "name", "price", "date"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Наименование")
    tree.heading("price", text="Сумма")
    tree.heading("date", text="Дата")
    tree.pack()

    # Function for opening the edit expense modal
    def open_edit_expense_modal(item_id, current_name, current_amount, current_date_time):
        edit_expense_modal = tk.Toplevel(frame)
        edit_expense_modal.title("Редактировать расход")

        tk.Label(edit_expense_modal, text="Наименование:").pack()
        name_entry = tk.Entry(edit_expense_modal)
        name_entry.pack()
        name_entry.insert(0, current_name)

        tk.Label(edit_expense_modal, text="Сумма:").pack()
        amount_entry = tk.Entry(edit_expense_modal)
        amount_entry.pack()
        amount_entry.insert(0, current_amount)

        tk.Label(edit_expense_modal, text="Дата и время (гггг-мм-дд чч:мм:сс):").pack()
        datetime_entry = tk.Entry(edit_expense_modal)
        datetime_entry.pack()

        # Предзаполнение поля текущими данными
        if isinstance(current_datetime, str):
            current_datetime = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S')
        datetime_entry.insert(0, current_datetime.strftime("%Y-%m-%d %H:%M:%S"))



        def save_edits():
            new_name = name_entry.get()
            new_amount = amount_entry.get()
            new_datetime_str = datetime_entry.get()

            if not new_name or not new_amount or not new_datetime_str:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                return

            try:
                new_amount = float(new_amount)
                new_datetime = datetime.strptime(new_datetime_str, "%Y-%m-%d %H:%M:%S")
                update_expense(item_id, new_name, new_amount, new_datetime)
                messagebox.showinfo("Успех", "Расход обновлен успешно.")
                edit_expense_modal.destroy()
                display_expenses_data()
            except ValueError:
                messagebox.showerror("Некорректно", "Введите корректную дату и время в формате гггг-мм-дд чч:мм:сс, и сумма должна быть числом.")

        tk.Button(edit_expense_modal, text="Сохранить", command=save_edits).pack()

    # Event for double-click to edit
    def on_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            item_id = tree.item(selected_item, "values")[0]
            current_name = tree.item(selected_item, "values")[1]
            current_amount = tree.item(selected_item, "values")[2]
            current_date = tree.item(selected_item, "values")[3]

            if isinstance(current_date, str):
                current_date = datetime.strptime(current_date, '%Y-%m-%d').date()

            open_edit_expense_modal(item_id, current_name, current_amount, current_date)

    tree.bind("<Double-1>", on_double_click)

    # Pagination variables
    current_page = tk.IntVar(value=1)
    records_per_page = tk.IntVar(value=10)

    tk.Label(frame, text="Записей на страницу:").pack()
    records_per_page_combobox = ttk.Combobox(frame, textvariable=records_per_page, state="readonly", values=[10, 25, 50, 100])
    records_per_page_combobox.pack()

    pagination_frame = tk.Frame(frame)
    pagination_frame.pack()

    def display_expenses_data():
        for item in tree.get_children():
            tree.delete(item)

        all_data = fetch_expenses_data()

        # Filter by expense name
        search_name = search_name_entry.get().lower()
        if search_name:
            all_data = [row for row in all_data if row[1] and search_name in row[1].lower()]

        # Filter by expense price
        search_price = search_price_entry.get()
        if search_price:
            try:
                search_price = float(search_price)
                all_data = [row for row in all_data if row[2] and row[2] == search_price]
            except ValueError:
                messagebox.showerror("Неправильно заполнено", "Сумма должна быть числом")
                return

        # Filter by date range
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        all_data = [row for row in all_data if start_date <= row[3] <= end_date]

        # Pagination logic
        total_pages = (len(all_data) - 1) // records_per_page.get() + 1
        if current_page.get() > total_pages:
            current_page.set(total_pages)
        elif current_page.get() < 1:
            current_page.set(1)

        start_index = (current_page.get() - 1) * records_per_page.get()
        end_index = start_index + records_per_page.get()
        paginated_data = all_data[start_index:end_index]

        for row in paginated_data:
            tree.insert("", tk.END, values=row)

        update_pagination_buttons(total_pages)

    # Filter and clear buttons
    tk.Button(frame, text="Поиск", command=display_expenses_data).pack()

    def clear_filters():
        search_name_entry.delete(0, tk.END)
        search_price_entry.delete(0, tk.END)
        start_date_entry.set_date(datetime.today().date())
        end_date_entry.set_date(datetime.today().date())
        display_expenses_data()

    tk.Button(frame, text="Очистить фильтры", command=clear_filters).pack()

    # Function to add a new expense
    def open_add_expense_modal():
        add_expense_modal = tk.Toplevel(frame)
        add_expense_modal.title("Добавить расход")

        tk.Label(add_expense_modal, text="Наименование:").pack()
        name_entry = tk.Entry(add_expense_modal)
        name_entry.pack()

        tk.Label(add_expense_modal, text="Сумма:").pack()
        amount_entry = tk.Entry(add_expense_modal)
        amount_entry.pack()

        tk.Label(add_expense_modal, text="Дата:").pack()
        date_entry = DateEntry(add_expense_modal, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.pack()
        date_entry.set_date(datetime.today().date())

        def save_expense():
            name = name_entry.get()
            amount = amount_entry.get()
            date = date_entry.get_date()

            if not name or not amount:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                return

            try:
                amount = float(amount)
                add_expense(name, amount, date)
                messagebox.showinfo("Успех", "Расход добавлен успешно.")
                add_expense_modal.destroy()
                display_expenses_data()
            except ValueError:
                messagebox.showerror("Некорректно", "Сумма должна быть числом.")

        tk.Button(add_expense_modal, text="Сохранить", command=save_expense).pack()

    # Button to open the add expense modal
    tk.Button(frame, text="Добавить расход", command=open_add_expense_modal).pack()

    # Update pagination buttons
    def update_pagination_buttons(total_pages):
        for widget in pagination_frame.winfo_children():
            widget.destroy()

        if total_pages > 1:
            for i in range(1, total_pages + 1):
                button = tk.Button(pagination_frame, text=str(i), command=lambda i=i: go_to_page(i))
                button.pack(side='left')
                if i == current_page.get():
                    button.config(state="disabled")

    def go_to_page(page_number):
        current_page.set(page_number)
        display_expenses_data()

    # Event bindings
    records_per_page_combobox.bind("<<ComboboxSelected>>", lambda event: display_expenses_data())

    display_expenses_data()
    add_observer(display_expenses_data)

    return frame
