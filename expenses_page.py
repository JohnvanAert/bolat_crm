import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from database import fetch_expenses_data, add_expense, update_expense, remove_expense
from expenses_data import add_observer, update_expenses_data, get_expenses_data
from datetime import datetime
from tkcalendar import Calendar

def create_expenses_page(root):
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)

    # Search fields
    tk.Label(frame, text="Поиск по имени").pack()
    search_name_entry = ttk.Entry(frame)
    search_name_entry.pack()

    tk.Label(frame, text="Поиск по номеру").pack()
    search_price_entry = ttk.Entry(frame)
    search_price_entry.pack()

    # Переменные для хранения выбранных дат
    selected_start_date = tk.StringVar(value="Нажмите для выбора")
    selected_end_date = tk.StringVar(value="Нажмите для выбора")

    def open_calendar(entry_variable):
        def set_date():
            selected_date = calendar.get_date()
            entry_variable.set(selected_date)
            calendar_window.destroy()

        # Создаем модальное окно для выбора даты
        calendar_window = tk.Toplevel(root)
        calendar_window.title("Выбор даты")
        calendar_window.geometry("300x300")
        calendar_window.grab_set()  # Делаем окно модальным

        calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
        calendar.pack(pady=20)

        tk.Button(calendar_window, text="Выбрать", command=set_date).pack(pady=10)

    # Виджеты для выбора диапазона дат
    tk.Label(frame, text="Дата с").pack(padx=10, pady=5)
    ttk.Button(frame, textvariable=selected_start_date, command=lambda: open_calendar(selected_start_date)).pack()

    tk.Label(frame, text="Дата по").pack(padx=10, pady=5)
    ttk.Button(frame, textvariable=selected_end_date, command=lambda: open_calendar(selected_end_date)).pack()


    # Table for displaying expense data
    tree = ttk.Treeview(frame, columns=("id", "name", "price", "date"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Наименование")
    tree.heading("price", text="Сумма")
    tree.heading("date", text="Дата")
    tree.pack()

    def refresh_expenses_data():
        # Здесь должен быть код обновления данных в таблице расходов
        display_expenses_data()  # Обновляем данные в таблице
        frame.after(300000, refresh_expenses_data)  # Повторяем вызов через 5 минут

    # Function for opening the edit expense modal
    def open_edit_expense_modal(item_id, current_name, current_amount, current_datetime):
        edit_expense_modal = tk.Toplevel(frame)
        edit_expense_modal.title("Редактировать расход")
        
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


        tk.Label(edit_expense_modal, text="Наименование:").pack()
        name_entry = ttk.Entry(edit_expense_modal)
        name_entry.pack()
        name_entry.insert(0, current_name)
        name_entry.bind("<KeyRelease>", validate_only_letters)

        tk.Label(edit_expense_modal, text="Сумма:").pack()
        amount_entry = ttk.Entry(edit_expense_modal)
        amount_entry.pack()
        amount_entry.insert(0, current_amount)
        amount_entry.bind("<KeyRelease>", validate_only_numbers)
        
            # Поле для редактирования даты
        tk.Label(edit_expense_modal, text="Дата (гггг-мм-дд):").pack()
        date_entry = ttk.Entry(edit_expense_modal)
        date_entry.pack()

        # Поле для редактирования времени
        tk.Label(edit_expense_modal, text="Время (чч:мм:сс):").pack()
        time_entry = ttk.Entry(edit_expense_modal)
        time_entry.pack()

        # Предзаполнение полей текущими данными
        if isinstance(current_datetime, str):
            current_datetime = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S')

        date_entry.insert(0, current_datetime.strftime("%Y-%m-%d"))
        time_entry.insert(0, current_datetime.strftime("%H:%M:%S"))

        def save_edits():
            new_name = name_entry.get()
            new_amount = amount_entry.get()
            new_date_str = date_entry.get()
            new_time_str = time_entry.get()

            if not new_name or not new_amount or not new_date_str or not new_time_str:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                return

            try:
                new_amount = float(new_amount)
                new_datetime_str = f"{new_date_str} {new_time_str}"
                new_datetime = datetime.strptime(new_datetime_str, "%Y-%m-%d %H:%M:%S")
                update_expense(item_id, new_name, new_amount, new_datetime)
                messagebox.showinfo("Успех", "Расход обновлен успешно.")
                edit_expense_modal.destroy()
                display_expenses_data()
            except ValueError:
                messagebox.showerror("Некорректно", "Введите корректную дату и время в формате гггг-мм-дд чч:мм:сс, и сумма должна быть числом.")

        def delete_expense():
            response = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить этот расход?")
            if response:
                remove_expense(item_id)
                messagebox.showinfo("Успех", "Расход удален успешно.")
                edit_expense_modal.destroy()
                display_expenses_data()

        tk.Button(edit_expense_modal, text="Сохранить", command=save_edits).pack()
        tk.Button(edit_expense_modal, text="Удалить", command=delete_expense, fg="red").pack()
    # Event for double-click to edit
    def on_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            item_id = tree.item(selected_item, "values")[0]
            current_name = tree.item(selected_item, "values")[1]
            current_amount = tree.item(selected_item, "values")[2]
            current_datetime = tree.item(selected_item, "values")[3]

            if isinstance(current_datetime, str):
                current_datetime = datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S')


            open_edit_expense_modal(item_id, current_name, current_amount, current_datetime)

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
        try:
            start_date = datetime.strptime(selected_start_date.get(), "%Y-%m-%d").date()
            end_date = datetime.strptime(selected_end_date.get(), "%Y-%m-%d").date()

            if start_date and end_date:
                all_data = [row for row in all_data if start_date <= row[3].date() <= end_date]
        except ValueError:
            pass  # Если дата не выбрана или формат неверный, фильтрация не применяется


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
    ttk.Button(frame, text="Поиск", command=display_expenses_data).pack()

    def clear_filters():
        search_name_entry.delete(0, tk.END)
        search_price_entry.delete(0, tk.END)
        selected_start_date.set("Нажмите для выбора")
        selected_end_date.set("Нажмите для выбора")
        display_expenses_data()

    ttk.Button(frame, text="Очистить фильтры", command=clear_filters).pack()

    # Function to add a new expense
    # Function to add a new expense
    def open_add_expense_modal():
        add_expense_modal = tk.Toplevel(frame)
        add_expense_modal.title("Добавить расход")

        tk.Label(add_expense_modal, text="Наименование:").pack()
        name_entry = ttk.Entry(add_expense_modal)
        name_entry.pack()

        tk.Label(add_expense_modal, text="Сумма:").pack()
        amount_entry = ttk.Entry(add_expense_modal)
        amount_entry.pack()

        # Поле для выбора даты
        tk.Label(add_expense_modal, text="Дата:").pack()
        selected_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d")) 
        date_button = ttk.Button(
            add_expense_modal,
            text="Выбрать дату",
            command=lambda: open_calendar(selected_date_var)  # Открыть календарь
        )
        date_button.pack()
        # Отображение выбранной даты
        date_label = tk.Label(add_expense_modal, textvariable=selected_date_var)
        date_label.pack()
        
        tk.Label(add_expense_modal, text="Время (чч:мм:сс):").pack()
        time_entry = ttk.Entry(add_expense_modal)
        time_entry.pack()
        time_entry.insert(0, datetime.now().strftime("%H:%M:%S"))  # Предзаполнение текущим временем

        def open_calendar(entry_variable):
            def set_date():
                selected_date = calendar.get_date()
                entry_variable.set(selected_date)
                calendar_window.destroy()

            # Создаем модальное окно для выбора даты
            calendar_window = tk.Toplevel(root)
            calendar_window.title("Выбор даты")
            calendar_window.geometry("300x300")
            calendar_window.grab_set()  # Делаем окно модальным

            calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
            calendar.pack(pady=20)

            ttk.Button(calendar_window, text="Выбрать", command=set_date).pack(pady=10)
        
        def save_expense():
            name = name_entry.get()
            amount = amount_entry.get()
            date = selected_date_var.get()
            time = time_entry.get()

            if not name or not amount or not time:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                return

            try:
                amount = float(amount)
                datetime_combined = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
                add_expense(name, amount, datetime_combined)
                messagebox.showinfo("Успех", "Расход добавлен успешно.")
                add_expense_modal.destroy()
                display_expenses_data()
            except ValueError:
                messagebox.showerror("Некорректно", "Введите корректные дату и время, и сумма должна быть числом.")

        ttk.Button(add_expense_modal, text="Сохранить", command=save_expense).pack()

    # Button to open the add expense modal
    ttk.Button(frame, text="Добавить расход", command=open_add_expense_modal).pack()

    # Update pagination buttons
    def update_pagination_buttons(total_pages):
        for widget in pagination_frame.winfo_children():
            widget.destroy()
        
        max_buttons_to_display = 5
        current = current_page.get()
        
        start_page = max(1, current - max_buttons_to_display // 2)
        end_page = min(total_pages, start_page + max_buttons_to_display - 1)
        
        if start_page > 1:
            ttk.Button(pagination_frame, text="<<", command=lambda: go_to_page(1)).grid(row=0, column=0)
            ttk.Button(pagination_frame, text="<", command=lambda: go_to_page(current - 1)).grid(row=0, column=1)
        
        col = 2
        for page in range(start_page, end_page + 1):
            button = ttk.Button(pagination_frame, text=str(page), command=lambda page=page: go_to_page(page))
            button.grid(row=0, column=col)
            if page == current:
                button.config(state="disabled")
            col += 1

        if end_page < total_pages:
            ttk.Button(pagination_frame, text=">", command=lambda: go_to_page(current + 1)).grid(row=0, column=col)
            ttk.Button(pagination_frame, text=">>", command=lambda: go_to_page(total_pages)).grid(row=0, column=col + 1)
    def go_to_page(page_number):
        current_page.set(page_number)
        display_expenses_data()

    # Event bindings
    records_per_page_combobox.bind("<<ComboboxSelected>>", lambda event: display_expenses_data())

    display_expenses_data()
    add_observer(display_expenses_data)
    refresh_expenses_data()
    
    return frame
