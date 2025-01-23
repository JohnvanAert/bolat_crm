import tkinter as tk
from tkcalendar import DateEntry
from tkinter import messagebox, ttk
from database import insert_sales_data, fetch_sales_data, update_sales_data, fetch_products, update_product_stock, insert_order_product, get_products_for_sale, delete_product_from_sale, update_product_quantity, delete_sales, get_cabin_info_from_sale, recalculate_cabin_price, get_products_data_for_sale, update_total_sales, update_sale_total_price, add_product_to_sale, get_all_products, is_cabin_busy, get_cabin_price, add_rental_extension, get_extensions_for_sale, decrease_product_stock, fetch_products_from_db, increase_product_stock, update_product_stocks, get_available_quantity, fetch_rental_cost, get_service_state, get_discount_state
from cabin_data import add_observer, get_cabins_data
import datetime
from decimal import Decimal, InvalidOperation
from tkcalendar import Calendar
from datetime import timedelta

def create_gui_page(root):
    frame = tk.Frame(root)

    selected_cabin_id = tk.StringVar()
    tk.Label(frame, text="Выберите кабинку").grid(row=0, column=0)
    cabins_combo = ttk.Combobox(frame, textvariable=selected_cabin_id, state="readonly")
    cabins_combo.grid(row=0, column=1)
    # Поля для поиска
    tk.Label(frame, text="Поиск по имени").grid(row=1, column=0)
    search_name_entry = ttk.Entry(frame)
    search_name_entry.grid(row=1, column=1)

    tk.Label(frame, text="Поиск по номеру").grid(row=2, column=0)
    search_number_entry = ttk.Entry(frame)
    search_number_entry.grid(row=2, column=1)

        # Поля для выбора диапазона дат (модальное окно вместо DateEntry)
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

    tk.Label(frame, text="Дата с").grid(row=3, column=0)
    ttk.Button(frame, textvariable=selected_start_date, command=lambda: open_calendar(selected_start_date)).grid(row=3, column=1)

    tk.Label(frame, text="Дата по").grid(row=4, column=0)
    ttk.Button(frame, textvariable=selected_end_date, command=lambda: open_calendar(selected_end_date)).grid(row=4, column=1)


    tree = ttk.Treeview(frame, columns=("id", "name", "number", "cabins_count", "total_sales", "date", "end_date"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("cabins_count", text="Выбранная кабинка")
    tree.heading("total_sales", text="Общий чек")
    tree.heading("name", text="Имя")
    tree.heading("number", text="Номер")
    tree.heading("date", text="Дата и Время")
    tree.heading("end_date", text="Дата окончания")
    tree.grid(row=7, column=0, columnspan=2)

    # Переменные для пагинации
    current_page = tk.IntVar(value=1)
    records_per_page = tk.IntVar(value=10)

    tk.Label(frame, text="Записей на странице:").grid(row=5, column=0)
    records_per_page_combobox = ttk.Combobox(frame, textvariable=records_per_page, state="readonly", values=[10, 25, 50, 100])
    records_per_page_combobox.grid(row=5, column=1)

    pagination_frame = tk.Frame(frame)
    pagination_frame.grid(row=11, column=0, columnspan=2)

    # Создаем фрейм для квадратов кабинок
    cabins_frame = ttk.Frame(frame)
    cabins_frame.grid(row=12, column=0, columnspan=2, pady=10)

    def create_cabin_buttons():
        """Создает кнопки-квадраты для всех кабинок из базы данных."""
        # Очистка предыдущих кнопок
        for widget in cabins_frame.winfo_children():
            widget.destroy()

        # Получаем данные о всех кабинках из базы
        cabins_data = get_cabins_data()

        # Создаем кнопки для каждой кабинки
        for idx, cabin in enumerate(cabins_data):
            cabin_name = cabin.get("name", f"Кабинка {idx+1}")  # Защита от отсутствия имени
            cabin_price = cabin.get("price", 0)  # Цена кабинки (по умолчанию 0)
            button_label = f"{cabin_name} - {cabin_price} $"  # Формируем строку с названием и ценой

            # Создаем кнопку
            cabin_button = tk.Button(
                cabins_frame,
                text=cabin_name,
                width=10,
                height=5,
                relief=tk.RAISED,
                bg="red",  # Кнопки с красным фоном
                fg="white",
                command=lambda c=cabin: handle_cabin_click(c)  # При нажатии передаем данные кабинки
            )
            # Располагаем кнопки в сетке
            row, col = divmod(idx, 5)  # 5 - количество кнопок в строке
            cabin_button.grid(row=row, column=col, padx=5, pady=5)


    def handle_cabin_click(cabin):
        """Обработчик нажатия на кнопку кабинки."""
        cabin_name = cabin.get("name", "Неизвестная кабинка")
        cabin_price = cabin.get("price", 0)
        cabin_label = f"{cabin_name} - {cabin_price} $"  # Формируем строку в нужном формате

        # Передаем название и цену кабинки в open_add_modal
        open_add_modal(selected_cabin=cabin_label)



    # Обновление интерфейса при изменении данных в базе
    def on_cabin_data_update():
        """Функция вызывается при изменении данных кабинок в базе."""
        create_cabin_buttons()

    # Подписываемся на обновления данных кабинок
    add_observer(on_cabin_data_update)

    # Инициализация кнопок при первом запуске
    create_cabin_buttons()

    def update_cabins_combo():
        cabins_data = get_cabins_data()
        cabins_combo_values = [f"{cabin['name']} - {cabin['price']} $" for cabin in cabins_data]
        cabins_combo['values'] = cabins_combo_values

    update_cabins_combo()
    add_observer(update_cabins_combo)

    def display_sales_data():
        for item in tree.get_children():
            tree.delete(item)
        
        all_data = fetch_sales_data()

        # Получение выбранного имени кабинки для фильтрации
        selected_cabin = selected_cabin_id.get().split(" - ")[0] if selected_cabin_id.get() else None
        
        if selected_cabin:
            cabins_data = get_cabins_data()
            selected_cabin_id_value = next((cabin['id'] for cabin in cabins_data if cabin['name'] == selected_cabin), None)
            
            if selected_cabin_id_value is not None:
                # Фильтрация данных по ID кабинки
                all_data = [row for row in all_data if row[3] == selected_cabin_id_value]  # row[3] должен содержать ID кабинки
        
         # Фильтрация по диапазону дат
        try:
            start_date = datetime.datetime.strptime(selected_start_date.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(selected_end_date.get(), "%Y-%m-%d").date()

            if start_date and end_date:
                all_data = [row for row in all_data if start_date <= row[5].date() <= end_date]
        except ValueError:
            pass  # Если дата не выбрана или формат неверный, фильтрация не применяется



            # Фильтрация данных по имени и номеру
        search_name = search_name_entry.get().lower()
        search_number = search_number_entry.get()


        if search_name:
            all_data = [row for row in all_data if row[1] and search_name in row[1].lower()]

        if search_number:
            all_data = [row for row in all_data if row[2] and search_number in row[2]]

        
        total_pages = (len(all_data) - 1) // records_per_page.get() + 1

        if current_page.get() > total_pages:
            current_page.set(total_pages)
        elif current_page.get() < 1:
            current_page.set(1)

        start_index = (current_page.get() - 1) * records_per_page.get()
        end_index = start_index + records_per_page.get()
        paginated_data = all_data[start_index:end_index]

        for row in paginated_data:
            id, name, number, cabins_id, total_sales, date, cabin_price, end_date = row
            tree.insert("", tk.END, values=(id, name, number, cabins_id, total_sales, date, end_date))



        update_pagination_buttons(total_pages)
    # Кнопка для поиска
        ttk.Button(frame, text="Поиск", command=display_sales_data).grid(row=5, column=0, columnspan=2)

        # Кнопка для очистки полей поиска и фильтров
        def clear_filters():
            search_name_entry.delete(0, tk.END)
            search_number_entry.delete(0, tk.END)
            selected_cabin_id.set("не выбрано")
            selected_start_date.set("Нажмите для выбора")
            selected_end_date.set("Нажмите для выбора")
            display_sales_data()

        ttk.Button(frame, text="Очистить фильтр", command=clear_filters).grid(row=6, column=0, columnspan=2)

    

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
        display_sales_data()

    records_per_page_combobox.bind("<<ComboboxSelected>>", lambda event: display_sales_data())
    selected_cabin_id.trace("w", lambda *args: display_sales_data())  # Обработчик для обновления данных при выборе кабинки

    display_sales_data()

    def on_item_double_click(event):
        item = tree.selection()[0]
        selected_data = tree.item(item, "values")

        sale_id = selected_data[0]
        service_state = get_service_state(sale_id)
        discount_state = get_discount_state(sale_id)
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

        edit_window = tk.Toplevel(root)
        edit_window.geometry("1000x800")  # Увеличьте размер окна
        edit_window.title("Редактирование заказа")
        edit_window.grid_rowconfigure(4, weight=1)  # Для масштабирования таблицы
        edit_window.grid_columnconfigure(1, weight=1)

        tk.Label(edit_window, text="Имя").grid(row=0, column=0, padx=10, pady=10)
        edit_name_entry = tk.Entry(edit_window)
        edit_name_entry.grid(row=0, column=1, padx=10, pady=10)
        edit_name_entry.insert(0, selected_data[1])
        edit_name_entry.bind("<KeyRelease>", validate_only_letters)
        
        tk.Label(edit_window, text="Номер").grid(row=1, column=0, padx=10, pady=10)
        edit_number_entry = tk.Entry(edit_window)
        edit_number_entry.grid(row=1, column=1, padx=10, pady=10)
        edit_number_entry.insert(0, selected_data[2])
        edit_number_entry.bind("<KeyRelease>", validate_only_numbers)
        
        tk.Label(edit_window, text="Выберите кабинку").grid(row=2, column=0, padx=10, pady=10)
        edit_cabins_combo = ttk.Combobox(edit_window, state="readonly")
        edit_cabins_combo.grid(row=2, column=1, padx=10, pady=10)
        edit_cabins_combo['values'] = cabins_combo['values']

        # Добавляем выпадающий список времени
        tk.Label(edit_window, text="Продолжительность аренды").grid(row=3, column=0, padx=10, pady=10)
        time_combo = ttk.Combobox(edit_window, state="readonly")
        time_combo.grid(row=3, column=1, padx=10, pady=10)
        time_combo['values'] = ["30 минут", "1 час", "1 час 30 минут", "2 часа"]
        def calculate_new_end_date(start_date, duration):
            if duration == "30 минут":
                return start_date + timedelta(minutes=30)
            elif duration == "1 час":
                return start_date + timedelta(hours=1)
            elif duration == "1 час 30 минут":
                return start_date + timedelta(minutes=90)
            elif duration == "2 часа":
                return start_date + timedelta(hours=2)
            return start_date
        
        # Установка текущей кабинки
        selected_cabin = selected_data[3]
        edit_cabins_combo.set(selected_cabin)

            # Раздел для отображения товаров
        tk.Label(edit_window, text="Список заказов").grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        products_frame = tk.Frame(edit_window)
        products_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Загрузка товаров из базы данных
        sale_id = selected_data[0]
        products_data = get_products_for_sale(sale_id)  # Получение товаров для текущей продажи

        products_tree = ttk.Treeview(products_frame, columns=("ID", "Название", "Количество", "Цена"), show="headings")
        products_tree.pack(fill="both", expand=True)


        # Настройка столбцов
        products_tree.heading("ID", text="ID")
        products_tree.heading("Название", text="Название")
        products_tree.heading("Количество", text="Количество")
        products_tree.heading("Цена", text="Цена")

        products_tree.column("ID", width=50)
        products_tree.column("Название", width=200)
        products_tree.column("Количество", width=100)
        products_tree.column("Цена", width=100)

        # Заполнение данными
        for product in products_data:
            products_tree.insert("", "end", values=(product['id'], product['name'], product['quantity'], product['price']))

            # Новый раздел для продлений времени
        extensions_frame = tk.Frame(edit_window)
        extensions_frame.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        extensions_tree = ttk.Treeview(extensions_frame, columns=("ID", "Минуты", "Время"), show="headings")
        extensions_tree.pack(fill="both", expand=True)

            # Настройка столбцов для продлений
        extensions_tree.heading("ID", text="ID")
        extensions_tree.heading("Минуты", text="Добавленные минуты")
        extensions_tree.heading("Время", text="Время изменений")

        extensions_tree.column("ID", width=50)
        extensions_tree.column("Минуты", width=150)
        extensions_tree.column("Время", width=200)

        # Получение данных о продлениях из базы
        extensions_data = get_extensions_for_sale(sale_id)
        for extension in extensions_data:
            extensions_tree.insert("", "end", values=extension)

          # Функция для добавления продуктов
        def open_add_product_window():
            add_product_window(sale_id, products_tree)

        def add_product_window(sale_id, products_tree):
            """
            Модальное окно для добавления продуктов к продаже.
            """
            product_window = tk.Toplevel(root)
            product_window.title("Добавить продукты")

            tk.Label(product_window, text="Список доступных товаров").grid(row=0, column=0, columnspan=2)

            product_list = ttk.Treeview(product_window, columns=("ID", "Название", "Цена", "Количество"), show="headings")
            product_list.grid(row=1, column=0, columnspan=2)

            product_list.heading("ID", text="ID")
            product_list.heading("Название", text="Название")
            product_list.heading("Цена", text="Цена")
            product_list.heading("Количество", text="Количество")

            product_list.column("ID", width=50)
            product_list.column("Название", width=150)
            product_list.column("Цена", width=100)
            product_list.column("Количество", width=100)

            # Получаем все доступные продукты
            all_products = get_all_products()
            current_products = {p['id']: p['quantity'] for p in get_products_for_sale(sale_id)}

            for product in all_products:
                product_id, product_name, product_price, product_quantity = (
                    product['id'], product['name'], product['price'], product['quantity']
                )

                # Проверяем, есть ли продукт в текущей продаже
                if product_id in current_products:
                    # Если количество 0, делаем строку недоступной
                    if product_quantity == 0:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("disabled",)
                        )
                    else:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("existing",)
                        )
                else:
                    # Если количество 0, делаем строку недоступной
                    if product_quantity == 0:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("disabled",)
                        )
                    else:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity)
                        )

            # Настройка тегов для таблицы
            product_list.tag_configure("existing", background="green")
            product_list.tag_configure("disabled", background="lightgray", foreground="gray")

            # Функция для обработки выбора продукта
            def on_product_select(event):
                selected_item = product_list.selection()
                if selected_item:
                    # Разблокируем поле для ввода количества
                    quantity_entry.config(state="normal")
                else:
                    # Заблокируем поле для ввода количества
                    quantity_entry.config(state="disabled")
                    add_button.config(state="disabled")

            # Функция для обработки ввода количества
            def on_quantity_change(*args):
                try:
                    quantity = int(quantity_var.get())
                    if quantity > 0:
                        # Если количество введено корректно, разблокируем кнопку
                        add_button.config(state="normal")
                    else:
                        # Заблокируем кнопку, если количество <= 0
                        add_button.config(state="disabled")
                except ValueError:
                    # Заблокируем кнопку, если введено некорректное значение
                    add_button.config(state="disabled")
            # Обновленная функция для добавления продуктов
            def get_product_stock(product_id):
                # Перебираем элементы в product_list
                for child in product_list.get_children():
                    product = product_list.item(child, "values")
                    if int(product[0]) == product_id:
                        return int(product[3])  # Возвращаем доступное количество (столбец 3)
                return 0  # Если продукт не найден
            def on_close_window():
                # Возвращаем добавленные продукты в доступное количество
                for product_id, product_info in added_products.items():
                    original_stock = get_product_stock(product_id)  # Получаем текущее количество
                    restored_stock = original_stock + product_info["quantity"]  # Возвращаем добавленные
                    update_product_stocks(product_id, restored_stock)  # Обновляем доступное количество

                # Закрываем окно
                product_window.destroy()
            product_window.protocol("WM_DELETE_WINDOW", on_close_window)
            
            added_products = {}
            def add_or_update_product():
                selected_item = product_list.selection()
                if not selected_item:
                    messagebox.showerror("Ошибка", "Выберите продукт!")
                    return

                selected_product = product_list.item(selected_item[0], "values")
                product_id = int(selected_product[0])
                product_price = float(selected_product[2])
                available_quantity = int(selected_product[3])

                try:
                    # Получаем количество из поля ввода
                    quantity_to_add = int(quantity_entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректное количество!")
                    return

                if quantity_to_add <= 0:
                    messagebox.showerror("Ошибка", "Количество должно быть больше 0!")
                    return

                available_quantity_in_db = get_available_quantity(product_id)  # Реальное количество в базе данных
                quantity_already_in_order = added_products.get(product_id, {}).get("quantity", 0)  # Уже добавленное количество в заказе

                # Проверяем, хватает ли доступного количества
                if quantity_to_add + quantity_already_in_order > available_quantity_in_db:
                    messagebox.showerror("Ошибка", "Недостаточно доступного количества!")
                    return

                print(f"Добавляем: {quantity_to_add}, Уже в заказе: {quantity_already_in_order}, Доступно в базе: {available_quantity_in_db}")

                            # Обновляем добавленные продукты
                if product_id in added_products:
                    added_products[product_id]["quantity"] += quantity_to_add
                else:
                    added_products[product_id] = {
                        "name": product_name,
                        "price": product_price,
                        "quantity": quantity_to_add,
                    }

                if product_id in current_products:
                    new_quantity = current_products[product_id] + quantity_to_add
                    if new_quantity > available_quantity:
                        messagebox.showerror("Ошибка", "Недостаточно доступного количества!")
                        return

                    update_product_quantity(sale_id, product_id, new_quantity)
                    current_products[product_id] = new_quantity
                else:
                    add_product_to_sale(sale_id, product_id, quantity_to_add, product_price)
                    current_products[product_id] = quantity_to_add

                # Уменьшаем количество доступного продукта
                new_available_quantity = available_quantity - quantity_to_add
                update_product_stocks(product_id, new_available_quantity)

                update_sale_total_price(sale_id, product_price * quantity_to_add)
                refresh_products_tree(products_tree, sale_id)
                refresh_product_list(product_list, sale_id)
                quantity_entry.delete(0, tk.END)  # Очищаем поле ввода после добавления

                        # Создаем переменную для отслеживания количества
            quantity_var = tk.StringVar()
            quantity_var.trace_add("write", on_quantity_change)

            # Поле для ввода количества (изначально заблокировано)
            quantity_entry = tk.Entry(product_window, textvariable=quantity_var, width=10, state="disabled")
            quantity_entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

            # Функция для обработки выбора продукта
            def on_product_select(event):
                selected_item = product_list.selection()
                if selected_item:
                    quantity_entry.config(state="normal")  # Разблокируем поле для ввода
                else:
                    quantity_entry.config(state="disabled")  # Заблокируем поле для ввода
                    add_button.config(state="disabled")  # Заблокируем кнопку

            # Функция для обработки изменения количества
            def on_quantity_change():
                try:
                    quantity = int(quantity_var.get())
                    if quantity > 0:
                        add_button.config(state="normal")  # Разблокируем кнопку, если количество корректное
                    else:
                        add_button.config(state="disabled")  # Заблокируем кнопку
                except ValueError:
                    add_button.config(state="disabled")  # Заблокируем кнопку, если введено некорректное значение

            # Привязываем обработчик события выбора продукта
            product_list.bind("<<TreeviewSelect>>", on_product_select)
            
            # Кнопка "Добавить" (изначально заблокирована)
            add_button = ttk.Button(product_window, text="Добавить", command=add_or_update_product, state="disabled")
            add_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
            # Кнопка "Закрыть"
            ttk.Button(product_window, text="Закрыть", command=product_window.destroy).grid(row=2, column=2, padx=10, pady=10, sticky="ew")
                        # Привязываем событие выбора продукта
            product_list.bind("<<TreeviewSelect>>", on_product_select)
        
        def delete_product():
            """Удаляет выбранный товар из заказа."""
            selected_item = products_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите товар для удаления!")
                return

            product_data = products_tree.item(selected_item[0], "values")
            product_id = product_data[0]  # ID товара
            product_quantity = int(product_data[2])
            cabin_id, cabin_price = get_cabin_info_from_sale(sale_id)  # Получаем ID кабинки и её стоимость

            if cabin_id is None:
                messagebox.showerror("Ошибка", "Не удалось получить данные о кабинке!")
                return

            response = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить товар?")
            if response:   
                # Увеличиваем количество товара на складе перед удалением
                increase_product_stock(product_id, product_quantity)
                
                delete_product_from_sale(sale_id, product_id)  # Удаление товара из базы данных
                refresh_products_tree(products_tree, sale_id)  # Обновление списка товаров
                recalculate_total_price(sale_id, cabin_price)  # Пересчет общей цены заказа
                recalculate_cabin_price(cabin_id)  # Пересчет стоимости кабинки

        def decrease_quantity():
            """Уменьшает количество выбранного товара."""
            selected_item = products_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите товар для уменьшения количества!")
                return

            product_data = products_tree.item(selected_item[0], "values")
            product_id, current_quantity = product_data[0], int(product_data[2])
            cabin_id, cabin_price = get_cabin_info_from_sale(sale_id)  # Получаем ID кабинки и её стоимость

            if cabin_id is None:
                messagebox.showerror("Ошибка", "Не удалось получить данные о кабинке!")
                return

            if current_quantity <= 1:
                delete_product()  # Удалить товар, если количество становится 0
            else:
                update_product_quantity(sale_id, product_id, current_quantity - 1)  # Уменьшение количества
                refresh_products_tree(products_tree, sale_id)  # Обновление списка товаров
                recalculate_total_price(sale_id, cabin_price)  # Пересчет общей цены заказа
                recalculate_cabin_price(cabin_id)  # Пересчет стоимости кабинки


        def refresh_products_tree(products_tree, sale_id=None):
            # Очистка текущих данных из таблицы
            for item in products_tree.get_children():
                products_tree.delete(item)

            # Получение актуальных данных из базы данных
            if sale_id:
                products_data = get_products_for_sale(sale_id)  # Используется из database.py
            else:
                products_data = fetch_products()  # Используется из database.py

            # Заполнение TreeView новыми данными
            for product in products_data:
                products_tree.insert(
                    "",
                    "end",
                    values=(product['id'], product['name'], product['quantity'], product['price'])
                )

        def refresh_product_list(product_list, sale_id):
            """
            Обновить список доступных продуктов в интерфейсе на основе текущих данных из БД.
            """
            # Получаем все продукты и текущие продукты для продажи
            all_products = get_all_products()
            current_products = {p['id']: p['quantity'] for p in get_products_for_sale(sale_id)}

            # Очищаем интерфейсный список
            for item in product_list.get_children():
                product_list.delete(item)

            # Перезаполняем список доступными продуктами
            for product in all_products:
                product_id, product_name, product_price, product_quantity = (
                    product['id'], product['name'], product['price'], product['quantity']
                )

                # Проверяем, доступен ли продукт
                if product_quantity <= 0:
                    product_list.insert(
                        "",
                        "end",
                        values=(product_id, product_name, product_price, product_quantity),
                        tags=("disabled",)
                    )
                else:
                    if product_id in current_products:
                        # Если продукт уже есть в текущей продаже
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("existing",)
                        )
                    else:
                        # Продукт доступен, но ещё не добавлен в продажу
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity)
                        )

            # Настройка тегов для отображения
            product_list.tag_configure("existing", background="green")
            product_list.tag_configure("disabled", background="lightgray", foreground="gray")


        def save_changes():
            new_name = edit_name_entry.get().strip()
            new_number = edit_number_entry.get().strip()
            service_charge_applied = bool(service_var.get())
            discount_applied = bool(discount_var.get())
            # Проверяем, выбрано ли новое значение из комбобокса
            if edit_cabins_combo.get():
                # Извлекаем только название кабинки (до дефиса)
                new_cabin = edit_cabins_combo.get().split(' - ')[0].strip().lower()
            else:
                new_cabin = selected_cabin.strip().lower()  # Используем старое значение, если новое не выбрано

            # Получаем данные о кабинках
            cabins_data = get_cabins_data()

            # Определяем новую кабинку и её цену
            selected_cabin_id = next((cabin['id'] for cabin in cabins_data if cabin['name'].strip().lower() == new_cabin), None)
            new_cabin_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['name'].strip().lower() == new_cabin), None)

            selected_cabin_id = int(selected_data[3])  # ID текущей кабинки
            cabin_hourly_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['id'] == selected_cabin_id), None)
            if not cabin_hourly_price:
                messagebox.showerror("Ошибка", "Не удалось получить цену кабинки!")
                return
            # Рассчитываем новую дату завершения
            duration = time_combo.get()
            # Рассчитываем продолжительность в часах
            duration_hours = {
                "30 минут": 0.5,
                "1 час": 1,
                "1 час 30 минут": 1.5,
                "2 часа": 2
            }.get(duration, 0)

            # Добавляем стоимость за дополнительное время к уже существующей цене
            cabin_total_price = Decimal(selected_data[6]) + (cabin_hourly_price * Decimal(duration_hours))

            # Если кабинка не найдена, используем прежние данные
            if selected_cabin_id is None or new_cabin_price is None:
                selected_cabin_id = selected_data[3]  # Прежний ID кабинки
                cabin_price = Decimal(selected_data[4])  # Прежняя цена кабинки
            else:
                cabin_price = new_cabin_price  # Новая цена кабинки

            try:
                 # Считаем старую дату завершения
                old_end_date = datetime.datetime.strptime(selected_data[5], '%Y-%m-%d %H:%M:%S')

                
                new_end_date = calculate_new_end_date(old_end_date, duration)

                # Вычисляем разницу во времени в минутах
                extension_minutes = int((new_end_date - old_end_date).total_seconds() / 60)
                add_rental_extension(
                    order_id=selected_data[0],  # ID заказа
                    extended_minutes=extension_minutes,  # Количество дополнительных минут
                )
            
            except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при расчете новой даты: {e}")
                    return
            
            # Проверка имени и номера на корректность
            if not new_name:
                messagebox.showerror("Ошибка", "Имя не может быть пустым!")
                return

            # Получаем данные о продуктах
            products_data = get_products_for_sale(selected_data[0])

            # Проверяем сумму продуктов
            total_products_price = sum(
                Decimal(product['price']) * Decimal(product['quantity']) for product in products_data
            ) if products_data else Decimal(0)

            # Общая сумма = сумма продуктов + цена кабинки
            if new_cabin == selected_cabin.strip().lower():
                cabin_price = Decimal(selected_data[6])  # Используем старую цену кабинки

            total_price = total_products_price + cabin_total_price

            # Добавляем или убираем 15% услуг
            if service_charge_applied:
                total_price *= Decimal(1.15)  # Прибавляем 15%
            else:
                if 'service_charge' in selected_data and selected_data['service_charge']:
                    total_price /= Decimal(1.15)  # Убираем 15%, если ранее был добавлен

            # Добавляем или убираем скидку 15%
            if discount_applied:
                total_price *= Decimal(0.85)  # Уменьшаем на 15%
            else:
                if 'discount_applied' in selected_data and selected_data['discount_applied']:
                    total_price /= Decimal(0.85)  # Возвращаем стоимость, если ранее скидка была применена

                    
            # Проверяем корректность значения общей суммы в selected_data
            try:
                previous_total_price = Decimal(selected_data[4])
            except (ValueError, TypeError, InvalidOperation):
                messagebox.showerror("Ошибка", "Некорректное значение общей суммы в данных! Попробуйте еще раз.")
                return

            # Сравниваем старую и новую суммы
            if total_price != previous_total_price:
                print(f"Сумма изменилась: {previous_total_price} → {total_price}")

            # Проверка имени и номера на корректность
            if not new_name:
                messagebox.showerror("Ошибка", "Имя не может быть пустым!")
                return

            if not new_number.isdigit():
                messagebox.showerror("Ошибка", "Номер должен быть числом!")
                return

            # Обновляем данные в базе
            update_sales_data(selected_data[0], new_name, new_number, selected_cabin_id, total_price.quantize(Decimal('0.01')), cabin_total_price, extension_minutes, service_charge_applied, discount_applied=discount_var.get())

            # Уведомление об успешном обновлении
            messagebox.showinfo("Успех", "Данные успешно обновлены!")

            # Обновить интерфейс
            display_sales_data()

            # Закрыть окно редактирования
            edit_window.destroy()


        def recalculate_total_price(sale_id, cabin_price):
            """
            Пересчитывает общую сумму продажи.
            Использует данные о товарах и стоимости кабинки.
            """
            try:
                # Получаем данные о продуктах через database.py
                products_data = get_products_data_for_sale(sale_id)
                
                # Считаем общую стоимость товаров
                total_products_price = sum(
                    Decimal(product['price']) * Decimal(product['quantity']) for product in products_data
                )
                
                # Если товаров нет, общая цена заказа должна быть 0
                total_price = total_products_price + cabin_price
                
                # Обновляем общую стоимость продажи через database.py
                update_total_sales(sale_id, total_price)
                
                print(f"Recalculated: Products total: {total_products_price}, Cabin price: {cabin_price}, Total: {total_price}")
                return total_products_price, total_price
            except Exception as e:
                print(f"Ошибка при пересчете общей стоимости: {e}")
                return None, None
  

        def delete_sale():
            response = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить эту запись?")
            if response:
                delete_sales(selected_data[0])  # Call to delete the record from database
                messagebox.showinfo("Успех", "Запись успешно удалена!")
                display_sales_data()  # Refresh the data displayed in the table
                edit_window.destroy()
        
        # Создаем фрейм для кнопок
        button_frame = tk.Frame(edit_window)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)  # Используем grid для размещения фрейма

        # Добавляем первый ряд кнопок
        ttk.Button(button_frame, text="Добавить продукты", command=open_add_product_window).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Удалить товар", command=delete_product, fg="red").grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Уменьшить количество", command=decrease_quantity).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Сохранить", command=save_changes, bg="green").grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Удалить", command=delete_sale, fg="red").grid(row=0, column=4, padx=5)

        # Боковая панель
        checkbox_frame = tk.Frame(edit_window)
        checkbox_frame.grid(row=10, column=0, columnspan=2, pady=5)  # Размещаем выше кнопок


        # Добавляем второй ряд чекбоксов и кнопок
        service_var = tk.BooleanVar(value=service_state)  # Переменная для состояния процента услуг
        discount_var = tk.BooleanVar(value=discount_state)  # Переменная для состояния скидки 15%

        tk.Checkbutton(checkbox_frame, text="Включить % услуг", variable=service_var).grid(row=1, column=0, columnspan=2, padx=5)
        tk.Checkbutton(checkbox_frame, text="Скидка 15%", variable=discount_var).grid(row=1, column=2, columnspan=2, padx=5)
        finish_order_button = tk.Button(checkbox_frame, text="Чек", bg="green", fg="white", command=lambda: show_final_receipt(selected_data, products_data, service_var.get(), discount_var.get()))
        finish_order_button.grid(row=1, column=4, columnspan=3, pady=5)

        def show_final_receipt(selected_data, products_data, service_state, discount_state):
            # Создаем модальное окно для отображения чека
            receipt_window = tk.Toplevel(edit_window)
            receipt_window.title("Чек")
            receipt_window.geometry("500x400")

            # Общая информация
            tk.Label(receipt_window, text=f"Клиент: {selected_data[1]}").pack(pady=5)
            tk.Label(receipt_window, text=f"Номер телефона: {selected_data[2]}").pack(pady=5)
            tk.Label(receipt_window, text=f"Кабинка: {selected_data[3]}").pack(pady=5)

            # Подсчет общей суммы за продукты
            total_product_cost = sum([
                Decimal(product['quantity']) * Decimal(product['price']) for product in products_data
            ])

            # Получение данных о стоимости аренды из базы
            try:
                rental_cost = fetch_rental_cost(selected_data[0])  # Используем ID продажи для запроса
                if rental_cost is None:
                    messagebox.showerror("Ошибка", "Не удалось получить данные о стоимости аренды!")
                    return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при получении данных из базы: {e}")
                return

            # Расчет общего чека
            total_cost = total_product_cost + Decimal(rental_cost)
            if service_state:  # Если включен процент услуг
                service_fee = total_cost * Decimal('0.15')  # Используем Decimal для 10% услуги
                total_cost += service_fee
            else:
                service_fee = Decimal('0')
            
            # Расчет скидки, если включена
            if discount_state:
                discount = total_cost * Decimal('0.15')  # Вычисляем 15% скидки
                total_cost -= discount
            else:
                discount = Decimal('0')


            # Отображение данных в чеке
            tk.Label(receipt_window, text="Заказанные продукты:").pack(pady=5)
            for product in products_data:
                tk.Label(receipt_window, text=f"{product['name']} x {product['quantity']} = {Decimal(product['quantity']) * Decimal(product['price']):.2f}").pack()

            tk.Label(receipt_window, text=f"Сумма за продукты: {total_product_cost:.2f}").pack(pady=5)
            tk.Label(receipt_window, text=f"Сумма за аренду кабины: {Decimal(rental_cost):.2f}").pack(pady=5)

            if service_state:
                tk.Label(receipt_window, text=f"Процент за услуги: {service_fee:.2f}").pack(pady=5)
            if discount_state:
                tk.Label(receipt_window, text=f"Скидка: {discount:.2f}").pack(pady=5)    
            tk.Label(receipt_window, text=f"Итоговая сумма: {total_cost:.2f}", font=("Arial", 14, "bold")).pack(pady=10)
            
            # Кнопка закрытия окна  
            close_button = tk.Button(receipt_window, text="Закрыть", command=receipt_window.destroy)
            close_button.pack(pady=10)



    tree.bind("<Double-1>", on_item_double_click)


    display_sales_data()

    def open_add_modal(selected_cabin=None):
        add_window = tk.Toplevel(root)
        add_window.title("Добавить запись")

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


        tk.Label(add_window, text="Имя").grid(row=0, column=0)
        entry_name = ttk.Entry(add_window)
        entry_name.grid(row=0, column=1)
        entry_name.bind("<KeyRelease>", validate_only_letters)

        tk.Label(add_window, text="Номер").grid(row=1, column=0)
        entry_number = ttk.Entry(add_window)
        entry_number.grid(row=1, column=1)
        entry_number.bind("<KeyRelease>", validate_only_numbers)

        tk.Label(add_window, text="Выберите кабинку").grid(row=2, column=0)
        cabins_combo_modal = ttk.Combobox(add_window, state="readonly")
        cabins_combo_modal.grid(row=2, column=1)
        cabins_combo_modal['values'] = cabins_combo['values']

        if selected_cabin:
            # Устанавливаем выбранную кабинку и блокируем список
            cabins_combo_modal.set(selected_cabin)
            cabins_combo_modal.config(state="disabled")
        else:
            # Разблокируем список, если кабинка не выбрана
            cabins_combo_modal.config(state="readonly")

        tk.Label(add_window, text="Общая продажа").grid(row=3, column=0)
        entry_sales = ttk.Entry(add_window, state='readonly')
        entry_sales.grid(row=3, column=1)

        # Поле для ввода времени аренды (в часах)
        tk.Label(add_window, text="На сколько часов?").grid(row=4, column=0)
        entry_hours = ttk.Entry(add_window)
        entry_hours.grid(row=4, column=1)
        

         # Обновление цены аренды на основе введенного времени
        def update_rental_price(event=None):
            try:
                hours = float(entry_hours.get())
                selected_cabin = cabins_combo_modal.get().split(" - ")[0]
                cabins_data = get_cabins_data()
                cabin_price = Decimal(0)
                for cabin in cabins_data:
                    if cabin['name'] == selected_cabin:
                        cabin_price = Decimal(cabin['price'])
                        break

                # Минимальная стоимость за первый час и половина стоимости за каждые последующие 30 минут
                total_rental_price = cabin_price * int(hours)  # Полные часы
                if hours % 1 > 0:
                    total_rental_price += (cabin_price / 2)  # Половина стоимости за дополнительные 30 минут

                # Обновляем поле Общая продажа
                total_price = total_rental_price + Decimal(total_product_price)
                entry_sales.config(state='normal')
                entry_sales.delete(0, tk.END)
                entry_sales.insert(0, round(total_price, 2))
                entry_sales.config(state='readonly')

                global total_cabin_rental  # Use a global variable or other method to pass this value
                total_cabin_rental = float(total_rental_price)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное количество часов.")

        # Привязка обновления стоимости к изменению часов
        entry_hours.bind("<KeyRelease>", update_rental_price)

        selected_products = {}
        total_product_price = 0

        selected_products_tree = ttk.Treeview(add_window, columns=("product_name", "price", "quantity"), show="headings")
        selected_products_tree.heading("product_name", text="Название")
        selected_products_tree.heading("price", text="Цена")
        selected_products_tree.heading("quantity", text="Количество")
        selected_products_tree.grid(row=6, column=0, columnspan=2)

        def open_product_list():
            nonlocal total_product_price

            product_window = tk.Toplevel(add_window)
            product_window.title("Выбор продуктов")

            product_tree = ttk.Treeview(product_window, columns=("product_id", "product_name", "price", "quantity"), show="headings")
            product_tree.heading("product_id", text="ID")
            product_tree.heading("product_name", text="Название")
            product_tree.heading("price", text="Цена")
            product_tree.heading("quantity", text="Количество")
            product_tree.pack(fill="both", expand=True)
            
            # Получение списка продуктов и отображение их в таблице
            products = fetch_products()
            for product in products:
             product_tree.insert("", tk.END, values=(product['id'], product['name'], product['price'], product['quantity']))
             # Поле для ввода количества
            quantity_label = tk.Label(product_window, text="Количество:")
            quantity_label.pack(side="left", padx=5, pady=5)

            quantity_entry = ttk.Entry(product_window, width=5)
            quantity_entry.pack(side="left", padx=5, pady=5)

            # Функция для обновления состояния кнопки
            def update_add_button_state(*args):
                if quantity_entry.get().isdigit() and int(quantity_entry.get()) > 0:
                    add_button.config(state="normal")
                else:
                    add_button.config(state="disabled")

            # Связываем событие изменения текста в поле ввода с проверкой
            quantity_entry.bind("<KeyRelease>", update_add_button_state)

            def refresh_product_tree():
                """Обновление таблицы с продуктами."""
                # Очистка текущего дерева
                for item in product_tree.get_children():
                    product_tree.delete(item)

                # Получение данных из базы
                products = fetch_products_from_db()  # Вызов функции из database.py
                for row in products:
                    product_tree.insert("", tk.END, values=row)

            def add_product_to_order():
                selected_item = product_tree.selection()
                if selected_item:
                    item_data = product_tree.item(selected_item)["values"]
                    if len(item_data) == 4:  # Проверка на наличие всех полей
                        product_id, product_name, price, stock = item_data
                        try:
                            quantity = int(quantity_entry.get())
                        except ValueError:
                            messagebox.showerror("Ошибка", "Введите корректное количество!")
                            return
                        
                        if quantity > stock:
                            messagebox.showerror("Ошибка", "Недостаточно товара на складе.")
                            return

                        if product_id in selected_products:
                            if selected_products[product_id]['quantity'] + quantity <= stock:
                                selected_products[product_id]['quantity'] += quantity
                            else:
                                messagebox.showerror("Ошибка", "Достигнуто максимальное количество для этого товара.")
                                return
                        else:
                            selected_products[product_id] = {
                                'name': product_name,
                                'price': price,
                                'quantity': quantity,
                                'stock': stock
                            }

                        # Уменьшение количества в базе данных
                        decrease_product_stock(product_id, quantity)

                        # Обновление дерева продуктов
                        refresh_product_tree()

                        # Обновление отображения выбранных продуктов
                        selected_products_tree.delete(*selected_products_tree.get_children())  # Очистка таблицы
                        for prod_id, prod_info in selected_products.items():
                            selected_products_tree.insert("", tk.END, values=(prod_info['name'], prod_info['price'], prod_info['quantity']))

                        update_total_price()
                        quantity_entry.delete(0, tk.END)  # Очистка поля после добавления
                        add_button.config(state="disabled")  # Блокируем кнопку
                    else:
                        messagebox.showerror("Ошибка", "Некорректные данные продукта!")
                else:
                    messagebox.showerror("Ошибка", "Выберите продукт!")


            def remove_product_from_order():
                selected_item = product_tree.selection()  # Получаем выбранный элемент
                if selected_item:
                    item_data = product_tree.item(selected_item)["values"]
                    product_name = item_data[1]  # Название продукта (второе значение в таблице)

                    for product_id, product_info in list(selected_products.items()):  # Проходим по словарю выбранных продуктов
                        if product_info['name'] == product_name:  # Находим нужный продукт по имени
                            # Увеличиваем количество продукта на складе на всё количество, которое было выбрано
                            increase_product_stock(product_id, product_info['quantity'])
                            
                            # Удаляем продукт из списка выбранных
                            del selected_products[product_id]
                            
                            # Обновляем отображение выбранных продуктов и таблицу
                            update_selected_products_tree()
                            update_product_table()
                            update_total_price()  # Обновляем общую стоимость
                            
                            return  # Завершаем выполнение после удаления продукта
                else:
                    messagebox.showerror("Ошибка", "Вы не выбрали продукт для удаления!")

            def update_selected_products_tree():
                # Очистка таблицы
                for i in selected_products_tree.get_children():
                    selected_products_tree.delete(i)

            def update_product_table():
                # Очистка таблицы перед обновлением
                product_tree.delete(*product_tree.get_children())

                # Получение актуального списка продуктов из базы данных
                updated_products = fetch_products()

                # Обновление таблицы
                for product in updated_products:
                    product_tree.insert("", tk.END, values=(product['id'], product['name'], product['price'], product['quantity']))

                # Добавление актуальных данных
                for product_id, product_info in selected_products.items():
                    selected_products_tree.insert(
                        "", tk.END,
                        values=(product_info['name'], product_info['price'], product_info['quantity'])
                    )

            def update_total_price():
                nonlocal total_product_price

                # Пересчитываем сумму продуктов заново, чтобы избежать дублирования
                total_product_price = sum(float(product['price']) * product['quantity'] for product in selected_products.values())

                # Получаем текущую цену кабинки (введенную при выборе) и используем ее только один раз
                if cabins_combo_modal.get():
                    selected_cabin_price_str = cabins_combo_modal.get().split(" - ")[1].replace(" $", "")
                    selected_cabin_price = float(selected_cabin_price_str)
                else:
                    selected_cabin_price = 0

                # Итоговая сумма включает одну цену кабинки и общую стоимость продуктов
                total_price = selected_cabin_price + total_product_price

                # Обновляем поле ввода с общей продажей
                entry_sales.config(state='normal')
                entry_sales.delete(0, tk.END)
                entry_sales.insert(0, round(total_price, 2))  # Округляем для точности
                entry_sales.config(state='readonly')

             # Кнопки
            add_button = ttk.Button(product_window, text="+ Добавить", command=add_product_to_order, state="disabled")
            add_button.pack(side="left", padx=5, pady=5)
            ttk.Button(product_window, text="- Удалить", command=remove_product_from_order).pack(side="left")
            ttk.Button(product_window, text="Закрыть", command=product_window.destroy).pack(side="right")

        ttk.Button(add_window, text="Выбрать продукты", command=open_product_list).grid(row=9, columnspan=2)


        def update_sales_price(event):
            selected = cabins_combo_modal.get().split(" - ")[0]
            cabins_data = get_cabins_data()
            cabin_price = Decimal(0)
            for cabin in cabins_data:
                if cabin['name'] == selected:
                    cabin_price = Decimal(cabin['price'])
                    entry_sales.config(state='normal')
                    entry_sales.delete(0, tk.END)

                    # Устанавливаем только цену кабинки при выборе
                    entry_sales.insert(0, cabin_price)
                    entry_sales.config(state='readonly')
                    break

        cabins_combo_modal.bind("<<ComboboxSelected>>", update_sales_price)

        def on_close():
            """Сброс всех временных изменений."""
            for product_id, product_info in selected_products.items():
                increase_product_stock(product_id, product_info['quantity'])
            add_window.destroy()

        add_window.protocol("WM_DELETE_WINDOW", on_close)
        def submit_data():
            name = entry_name.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Поле 'Имя' обязательно к заполнению.")
                return
            try:
                name = entry_name.get()
                number = entry_number.get()
                selected_cabin = cabins_combo_modal.get().split(" - ")[0]
                cabins_data = get_cabins_data()
                selected_cabin_id = next((cabin['id'] for cabin in cabins_data if cabin['name'] == selected_cabin), None)

                hours = float(entry_hours.get())
                current_time = datetime.datetime.now()
                end_date = current_time + timedelta(hours=hours)

                # Проверяем занятость кабины
                if is_cabin_busy(selected_cabin_id, current_time):
                    messagebox.showerror("Ошибка", "Эта кабина уже занята в данный момент.")
                    return

                cabin_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['name'] == selected_cabin), None)

                # Преобразуем total_product_price в Decimal
                total_product_price_decimal = Decimal(total_product_price)

                 # Получаем количество часов аренды
                hours = float(entry_hours.get())
                total_rental_price = cabin_price * int(hours)
                if hours % 1 > 0:
                    total_rental_price += (cabin_price / 2)

                # Общая сумма заказа
                total_price = total_rental_price + total_product_price_decimal

                # Вычисляем конечное время аренды
                start_date = datetime.datetime.now().replace(microsecond=0)
                end_date = start_date + timedelta(hours=hours)
                print(f"Products total: {total_product_price_decimal}, Cabin price: {cabin_price}, Total: {total_price}")
                # Сохраняем продажу и получаем ID
                sale_id = insert_sales_data(name, number, selected_cabin_id, total_price, start_date,  total_rental_price, end_date)
                
                # Сохраняем продукты, добавленные к заказу, в таблицу sales_products
                for product_id, product_info in selected_products.items():
                    insert_order_product(sale_id, product_id, product_info['quantity'], product_info['price'])

                # Обновление количества на складе
                for product_id, product_info in selected_products.items():
                    update_product_stock(product_id, product_info['quantity'])

                messagebox.showinfo("Успех", "Данные успешно добавлены!")
                display_sales_data()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

        ttk.Button(add_window, text="Добавить", command=submit_data).grid(row=8, columnspan=2)

    ttk.Button(frame, text="Добавить запись", command=lambda: open_add_modal()).grid(row=13, columnspan=2)


    return frame
